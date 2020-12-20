/// GPI_RP driver
///
/// (c) Koheron

#ifndef __DRIVERS_GPI_RP_HPP__
#define __DRIVERS_GPI_RP_HPP__

#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <queue>
#include <mutex>

#include <context.hpp>

// http://www.xilinx.com/support/documentation/ip_documentation/axi_fifo_mm_s/v4_1/pg080-axi-fifo-mm-s.pdf
namespace Fifo_regs {
    constexpr uint32_t rdfr = 0x18;
    constexpr uint32_t rdfo = 0x1C;
    constexpr uint32_t rdfd = 0x20;
    constexpr uint32_t rlr = 0x24;
}

constexpr uint32_t adc_buff_size = 50000;

class GPI_RP {
    public:
        GPI_RP(Context& ctx_)
        : ctx(ctx_)
        , ctl(ctx.mm.get<mem::control>())
        , sts(ctx.mm.get<mem::status>())
        , adc_fifo_map(ctx.mm.get<mem::adc_fifo>())
        , adc_data(adc_buff_size)
        {
            fifo_thread = std::thread{&GPI_RP::fifo_acquisition_thread, this};
        }

	~GPI_RP()
        {
            fifo_thread_running = false;
            fifo_thread.join();
        }

        // GPI_RP generator
        void set_led(uint32_t led) {
            ctl.write<reg::led>(led);
        }

        void set_analog_out(uint32_t analog_out) {
            ctl.write<reg::analog_out>(analog_out);
        }

        void set_GPI_safe_state(uint32_t state) {
            ctl.write<reg::GPI_safe_state>(state);
        }

        void set_slow_1(uint32_t state) {
            ctl.write<reg::slow_1_manual>(state);
        }

        void set_slow_2(uint32_t state) {
            ctl.write<reg::slow_2_manual>(state);
        }

        void set_slow_3(uint32_t state) {
            ctl.write<reg::slow_3_manual>(state);
        }

        void set_slow_4(uint32_t state) {
            ctl.write<reg::slow_4_manual>(state);
        }

        void set_fast(uint32_t state) {
            ctl.write<reg::fast_manual>(state);
        }

        void set_fast_permission_1(uint32_t state) {
            ctl.write<reg::fast_permission_1>(state);
        }

        void set_fast_duration_1(uint32_t state) {
            ctl.write<reg::fast_duration_1>(state);
        }

        void reset_time(uint32_t state) {
            ctl.write<reg::reset_time>(state);
        }

        void set_fast_delay_1(uint32_t state) {
            ctl.write<reg::fast_delay_1>(state);
        }

        void set_fast_delay_2(uint32_t state) {
            ctl.write<reg::fast_delay_2>(state);
        }

        void set_fast_permission_2(uint32_t state) {
            ctl.write<reg::fast_permission_2>(state);
        }

        void set_fast_duration_2(uint32_t state) {
            ctl.write<reg::fast_duration_2>(state);
        }

        void send_T1(uint32_t state) {
            ctl.write<reg::send_T1>(state);
        }

        uint32_t get_W7X_T1() {
            return sts.read<reg::W7X_T1>();
        }

        uint32_t get_analog_out() {
            return sts.read<reg::analog_out_sts>();
        }

        uint32_t get_abs_gauge() {
            return sts.read<reg::abs_gauge>();
        }

        uint32_t get_diff_gauge() {
            return sts.read<reg::diff_gauge>();
        }

        uint32_t get_analog_input_0() {
            return sts.read<reg::analog_input_0>();
        }

        uint32_t get_analog_input_1() {
            return sts.read<reg::analog_input_1>();
        }

        uint32_t get_slow_1_sts() {
            return sts.read<reg::slow_1_sts>();
        }

        uint32_t get_slow_2_sts() {
            return sts.read<reg::slow_2_sts>();
        }

        uint32_t get_slow_3_sts() {
            return sts.read<reg::slow_3_sts>();
        }

        uint32_t get_slow_4_sts() {
            return sts.read<reg::slow_4_sts>();
        }

        uint32_t get_fast_sts() {
            return sts.read<reg::fast_sts>();
        }

        // Adc FIFO

        uint32_t get_fifo_occupancy() {
           return adc_fifo_map.read<Fifo_regs::rdfo>();
        }

        void reset_fifo() {
            adc_fifo_map.write<Fifo_regs::rdfr>(0x000000A5);
        }

        uint32_t read_fifo() {
            return adc_fifo_map.read<Fifo_regs::rdfd>();
        }

        uint32_t get_fifo_length() {
           return (adc_fifo_map.read<Fifo_regs::rlr>() & 0x3FFFFF) >> 2;
        }

        /** return the buffer length */
        uint32_t get_buffer_length() {
            return adc_data_queue.size();
        }

        /** return data */
        std::vector<uint32_t>& get_GPI_data()
        {
            const std::lock_guard<std::mutex> lock(adc_data_queue_mutex);
            const size_t queue_count = adc_data_queue.size();
            adc_data.resize(queue_count);
            for (size_t i = 0; i < queue_count; i++) {
                adc_data[i] = adc_data_queue.front();
                adc_data_queue.pop();
            }
            return adc_data;
        }

        void wait_for(uint32_t n_pts)
        {
            while (get_fifo_length() < n_pts)
            { // sleep to keep cpu low
                usleep(100);
            }
        }

    private:
        Context& ctx;
        Memory<mem::control>& ctl;
        Memory<mem::status>& sts;
        Memory<mem::adc_fifo>& adc_fifo_map;

        std::mutex adc_data_queue_mutex;
        std::queue<uint32_t> adc_data_queue;
        std::vector<uint32_t> adc_data;

        void fill_buffer();

        std::thread fifo_thread;
        std::atomic<bool> fifo_thread_running{true};
        void fifo_acquisition_thread();
};

inline void GPI_RP::fifo_acquisition_thread()
{
    ctx.log<INFO>("Starting fifo acquisition");
    // While loop to reserve the number of samples needed to be collected
    while (fifo_thread_running)
    {
        fill_buffer();
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}

// Member function to fill buffer array
inline void GPI_RP::fill_buffer()
{
    // Retrieving the number of samples to collect
    const uint32_t samples = get_fifo_length();
    if (samples > 0)
    {
        const std::lock_guard<std::mutex> lock(adc_data_queue_mutex);
        for (size_t i=0; i < samples; i++)
        {
            if (adc_data_queue.size() == adc_buff_size)
                adc_data_queue.pop();
            adc_data_queue.push(read_fifo());
        }
    }
}


#endif // __DRIVERS_PCS_HPP__
