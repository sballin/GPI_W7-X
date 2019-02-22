/// GPI_2 driver
///
/// (c) Koheron

#ifndef __DRIVERS_GPI_2_HPP__
#define __DRIVERS_GPI_2_HPP__

#include <atomic>
#include <thread>
#include <chrono>
#include <queue>

#include <context.hpp>

// http://www.xilinx.com/support/documentation/ip_documentation/axi_fifo_mm_s/v4_1/pg080-axi-fifo-mm-s.pdf
namespace Fifo_regs {
    constexpr uint32_t rdfr = 0x18;
    constexpr uint32_t rdfo = 0x1C;
    constexpr uint32_t rdfd = 0x20;
    constexpr uint32_t rlr = 0x24;
}

//constexpr uint32_t dac_size = mem::dac_range/sizeof(uint32_t);
constexpr uint32_t adc_buff_size = 50000;

class GPI_2 {
  public:
    GPI_2(Context& ctx_)
    : ctx(ctx_)
    , ctl(ctx.mm.get<mem::control>())
    , sts(ctx.mm.get<mem::status>())
    , adc_fifo_map(ctx.mm.get<mem::adc_fifo>())
    , adc_data(adc_buff_size)
     {
        start_fifo_acquisition();
     }

    // GPI_2 generator
    void set_led(uint32_t led) {
        ctl.write<reg::led>(led);
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

    uint32_t get_abs_gauge() {
        return sts.read<reg::abs_gauge>();
    }

    uint32_t get_diff_gauge() {
        return sts.read<reg::diff_gauge>();
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

     // Function to return the buffer length
    uint32_t get_buffer_length() {
        ctx.log<INFO>("get_buffer_length");
        return adc_data_queue.size();
    }
    
    // string get_ctx() {
    //     return ctx;
    // }
    
    // Function to return data
    std::vector<uint32_t>& get_GPI_data() {
        if (dataAvailable) {
            adc_data.reserve(adc_data_queue.size());
            for (size_t i = 0; i < adc_data_queue.size(); i++) {
                adc_data[i] = adc_data_queue.front();
                adc_data_queue.pop();
            }
            dataAvailable = false;
            return adc_data;
        } else {
            return empty_vector;
        }
    }

    void wait_for(uint32_t n_pts) {
        do {} while (get_fifo_length() < n_pts);
    }

    void start_fifo_acquisition();

  private:
    Context& ctx;
    Memory<mem::control>& ctl;
    Memory<mem::status>& sts;
    Memory<mem::adc_fifo>& adc_fifo_map;
    // Memory<mem::dac>& dac_map;

    std::queue<uint32_t> adc_data_queue;
    std::vector<uint32_t> adc_data;
    std::vector<uint32_t> empty_vector;
    
    uint32_t fill_buffer(uint32_t);

    std::atomic<bool> fifo_acquisition_started{false};
    std::atomic<bool> dataAvailable{false};
    std::atomic<uint32_t> collected{0};         //number of currently collected data

    std::thread fifo_thread;
    void fifo_acquisition_thread();

};

inline void GPI_2::start_fifo_acquisition() {
    // if (! fifo_acquisition_started) {
    //     // fifo_buffer.fill(0);
    //     fifo_thread = std::thread{&GPI_2::fifo_acquisition_thread, this};
    //     fifo_thread.detach();
    // }
}

inline void GPI_2::fifo_acquisition_thread() {
    constexpr auto fifo_sleep_for = std::chrono::nanoseconds(5000);
    fifo_acquisition_started = true;
    ctx.log<INFO>("Starting fifo acquisition");
    // adc_data.reserve(16777216);
    // adc_data.resize(0);
    empty_vector.resize(0);
    
    // uint32_t dropped=0;
    
    // While loop to reserve the number of samples needed to be collected
    while (fifo_acquisition_started){
        // Checking that data has not yet been collected      
        if ((dataAvailable == false) && (adc_data.size() > 0)){
            // Sleep to avoid a race condition while data is being transferred
            std::this_thread::sleep_for(fifo_sleep_for);
            // Clearing vector back to zero
            // adc_data.resize(0);
            ctx.log<INFO>("vector cleared, adc_data size: %d", adc_data_queue.size());
        }
      
        // dropped = fill_buffer(dropped);
        // if (dropped > 0){
        //     ctx.log<INFO>("Dropped samples: %d", dropped);
        // }
        std::this_thread::sleep_for(fifo_sleep_for);
    }
}

// Member function to fill buffer array
inline uint32_t GPI_2::fill_buffer(uint32_t dropped) {
    // Retrieving the number of samples to collect
    uint32_t samples=get_fifo_length();
    ctx.log<INFO>("Samples: %d", samples); 
    
    // Collecting samples in buffer
    if (samples > 0) 
    {
        // Checking for dropped samples
        if (samples >= 32768)
        {    
            dropped += 1;
        }
        for (size_t i=0; i < samples; i++)
        {  
            adc_data_queue.push(read_fifo());    
            // collected = collected + 1;
        }
        while (adc_data_queue.size() > adc_buff_size)
        {
            adc_data_queue.pop();
        }
        dataAvailable = true; 
    }
    // if ((dataAvailable == false) && (adc_data.length() > 0))
    // {
    //     adc_data.resize(0);
    // }
    return dropped;
}


#endif // __DRIVERS_PCS_HPP__
