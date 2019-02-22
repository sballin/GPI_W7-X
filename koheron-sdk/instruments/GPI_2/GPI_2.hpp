/// GPI_2 driver
///
/// (c) Koheron

#ifndef __DRIVERS_GPI_2_HPP__
#define __DRIVERS_GPI_2_HPP__

#include <atomic>
#include <thread>
#include <chrono>

#include <context.hpp>

// http://www.xilinx.com/support/documentation/ip_documentation/axi_fifo_mm_s/v4_1/pg080-axi-fifo-mm-s.pdf
namespace Fifo_regs {
    constexpr uint32_t rdfr = 0x18;
    constexpr uint32_t rdfo = 0x1C;
    constexpr uint32_t rdfd = 0x20;
    constexpr uint32_t rlr = 0x24;
}

//constexpr uint32_t dac_size = mem::dac_range/sizeof(uint32_t);
constexpr uint32_t adc_buff_size = 16777216;

class GPI_2
{
  public:
    GPI_2(Context& ctx_)
    : ctx(ctx_)
    , ctl(ctx.mm.get<mem::control>())
    , sts(ctx.mm.get<mem::status>())
    , adc_fifo_map(ctx.mm.get<mem::adc_fifo>())
    , adc_data(adc_buff_size)
    // , dac_map(ctx.mm.get<mem::dac>())
    {
        start_fifo_acquisition();
    }

    // GPI_2 generator
    void set_led(uint32_t led) {
        ctl.write<reg::led>(led);
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
       return collected;
    }

    void set_GPI_safe_state(uint32_t state) {
        ctl.write<reg::GPI_safe_state>(state);
    }

    uint32_t get_GPI_safe_state() {
        return ctl.read<reg::GPI_safe_state>();
    }

    void set_slow_1_trigger(uint32_t state) {
        ctl.write<reg::slow_1_trigger>(state);
    }

    uint32_t get_slow_1_trigger() {
        return ctl.read<reg::slow_1_trigger>();
    }

    void set_slow_2_trigger(uint32_t state) {
        ctl.write<reg::slow_2_trigger>(state);
    }

    uint32_t get_slow_2_trigger() {
        return ctl.read<reg::slow_2_trigger>();
    }

    void set_slow_3_trigger(uint32_t state) {
        ctl.write<reg::slow_3_trigger>(state);
    }

    uint32_t get_slow_3_trigger() {
        return ctl.read<reg::slow_3_trigger>();
    }

    void set_slow_4_trigger(uint32_t state) {
        ctl.write<reg::slow_4_trigger>(state);
    }

    uint32_t get_slow_4_trigger() {
        return ctl.read<reg::slow_4_trigger>();
    }

    void set_fast_1_trigger(uint32_t state) {
        ctl.write<reg::fast_1_trigger>(state);
    }

    uint32_t get_fast_1_trigger() {
        return ctl.read<reg::fast_1_trigger>();
    }

    void set_fast_1_permission_1(uint32_t state) {
        ctl.write<reg::fast_1_permission_1>(state);
    }

    uint32_t get_fast_1_permission_1() {
        return ctl.read<reg::fast_1_permission_1>();
    }

    void set_fast_1_duration_1(uint32_t state) {
        ctl.write<reg::fast_1_duration_1>(state);
    }

    uint32_t get_fast_1_duration_1() {
        return ctl.read<reg::fast_1_duration_1>();
    }

    void set_fast_1_permission_2(uint32_t state) {
        ctl.write<reg::fast_1_permission_2>(state);
    }

    uint32_t get_fast_1_permission_2() {
        return ctl.read<reg::fast_1_permission_2>();
    }

    void set_fast_1_duration_2(uint32_t state) {
        ctl.write<reg::fast_1_duration_2>(state);
    }

    uint32_t get_fast_1_duration_2() {
        return ctl.read<reg::fast_1_duration_2>();
    }

    void set_fast_2_trigger(uint32_t state) {
        ctl.write<reg::fast_2_trigger>(state);
    }

    uint32_t get_fast_2_trigger() {
        return ctl.read<reg::fast_2_trigger>();
    }

    void set_fast_2_permission_1(uint32_t state) {
        ctl.write<reg::fast_2_permission_1>(state);
    }

    uint32_t get_fast_2_permission_1() {
        return ctl.read<reg::fast_2_permission_1>();
    }

    void set_fast_2_duration_1(uint32_t state) {
        ctl.write<reg::fast_2_duration_1>(state);
    }

    uint32_t get_fast_2_duration_1() {
        return ctl.read<reg::fast_2_duration_1>();
    }

    void set_fast_2_permission_2(uint32_t state) {
        ctl.write<reg::fast_2_permission_2>(state);
    }

    uint32_t get_fast_2_permission_2() {
        return ctl.read<reg::fast_2_permission_2>();
    }

    void set_fast_2_duration_2(uint32_t state) {
        ctl.write<reg::fast_2_duration_2>(state);
    }

    uint32_t get_fast_2_duration_2() {
        return ctl.read<reg::fast_2_duration_2>();
    }

    uint32_t get_W7X_permission() {
        return sts.read<reg::W7X_permission_in>();
    }

    uint32_t get_abs_gauge() {
        return sts.read<reg::abs_gauge>();
    }

    uint32_t get_diff_gauge() {
        return sts.read<reg::diff_gauge>();
    }
    
     // Function to return data
  std::vector<uint32_t>& get_GPI_2_data() {
    
    if (dataAvailable){
      dataAvailable = false;
          
      return adc_data;
    } else {
      return empty_vector;
    }
  }

    // void wait_for(uint32_t n_pts) {
    //     do {} while (get_fifo_length() < n_pts);
    // }



    void start_fifo_acquisition();

  private:
    Context& ctx;
    Memory<mem::control>& ctl;
    Memory<mem::status>& sts;
    Memory<mem::adc_fifo>& adc_fifo_map;
    // Memory<mem::dac>& dac_map;

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
    if (! fifo_acquisition_started) {
        // fifo_buffer.fill(0);
        fifo_thread = std::thread{&GPI_2::fifo_acquisition_thread, this};
        fifo_thread.detach();
    }
}

inline void GPI_2::fifo_acquisition_thread() {
  constexpr auto fifo_sleep_for = std::chrono::nanoseconds(5000);
  fifo_acquisition_started = true;
  ctx.log<INFO>("Starting fifo acquisition");
  adc_data.reserve(16777216);
  adc_data.resize(0);
  empty_vector.resize(0);
  
  uint32_t dropped=0;
  
  // While loop to reserve the number of samples needed to be collected
  while (fifo_acquisition_started){
    // if (dataAvailable == true) {
    //   ctx.log<INFO>("Reached checkpoint alpha");
    // } else {
    //   ctx.log<INFO>("Reached checkpoint charlie");
    // }
    if (collected == 0){
      // Checking that data has not yet been collected      
      if ((dataAvailable == false) && (adc_data.size() > 0)){
    // Sleep to avoid a race condition while data is being transferred
    std::this_thread::sleep_for(fifo_sleep_for);
    // Clearing vector back to zero
    adc_data.resize(0);
    ctx.log<INFO>("vector cleared, adc_data size: %d", adc_data.size());
      }
    }
    
    dropped = fill_buffer(dropped);
    if (dropped > 0){
      ctx.log<INFO>("Dropped samples: %d", dropped);
    }
    // std::this_thread::sleep_for(fifo_sleep_for);
  }// While loop
}

// Member function to fill buffer array
inline uint32_t GPI_2::fill_buffer(uint32_t dropped) {
    // Retrieving the number of samples to collect
  uint32_t samples=get_fifo_length();
  //ctx.log<INFO>("Samples: %d", samples); 
  
  // Collecting samples in buffer
  if (samples > 0) {
    // Checking for dropped samples
    if (samples >= 32768){    
      dropped += 1;
    }
    for (size_t i=0; i < samples; i++){   
      adc_data.push_back(read_fifo());    
      collected = collected + 1;
    }
  }
  // if statement for setting the acquisition completed flag
  if (samples == 0) {
    if (collected > 0) {
      dataAvailable = true;
      collected = 0;
      dropped = 0;
    }
  }
  return dropped;
}


#endif // __DRIVERS_PCS_HPP__
