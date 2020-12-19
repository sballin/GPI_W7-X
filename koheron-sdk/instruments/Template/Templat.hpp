/// Template driver
///
/// (c) Koheron

#ifndef __DRIVERS_PCS_HPP__
#define __DRIVERS_PCS_HPP__

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

constexpr uint32_t dac_size = mem::dac_range/sizeof(uint32_t);
constexpr uint32_t adc_buff_size = 16777216;

class Template
{
  public:
    Template(Context& ctx_)
    : ctx(ctx_)
    , ctl(ctx.mm.get<mem::control>())
    , sts(ctx.mm.get<mem::status>())
    , adc_fifo_map(ctx.mm.get<mem::adc_fifo>())
    , adc_data(adc_buff_size)
    // , dac_map(ctx.mm.get<mem::dac>())
    {
        start_fifo_acquisition();
    }

    // Template generator
    void set_led(uint32_t led) {
        ctl.write<reg::led>(led);
    }

    
    void set_reg1(uint32_t a_reg1) {
        ctl.write<reg::a_reg1>(a_reg1);
    }

     void set_reg2(uint32_t a_reg2) {
        ctl.write<reg::a_reg2>(a_reg2);
    }

    uint32_t get_a_reg1_s() {
        uint32_t a_reg1_s_value = sts.read<reg::a_reg1_s>();
        return a_reg1_s_value;
    } 

    uint32_t get_a_reg_2() {
        uint32_t a_reg2_s_value = sts.read<reg::a_reg2_s>();
        return a_reg2_s_value;
    } 

    // void set_dac_data(const std::array<uint32_t, dac_size>& data) {
    //     dac_map.write_array(data);
    // }

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

     // Function to return data
  std::vector<uint32_t>& get_Template_data() {
    
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

inline void Template::start_fifo_acquisition() {
    if (! fifo_acquisition_started) {
        // fifo_buffer.fill(0);
        fifo_thread = std::thread{&Template::fifo_acquisition_thread, this};
        fifo_thread.detach();
    }
}

inline void Template::fifo_acquisition_thread() {
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
inline uint32_t Template::fill_buffer(uint32_t dropped) {
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
