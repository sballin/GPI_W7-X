/// MLP driver
///
/// (c) Koheron

#ifndef __DRIVERS_MLP_HPP__
#define __DRIVERS_MLP_HPP__

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

class MLP {
public:
  MLP(Context& ctx_)
    : ctx(ctx_)
    , ctl(ctx.mm.get<mem::control>())
    , sts(ctx.mm.get<mem::status>())
    , adc_fifo_map(ctx.mm.get<mem::adc_fifo>())
    , adc_data(adc_buff_size)
  {
    start_fifo_acquisition();
  }
  
  //  MLP
  void set_led(uint32_t led) {
    ctl.write<reg::led>(led);
  }
  
  void set_trigger() {
    ctl.set_bit<reg::Trigger, 0>();
    ctl.clear_bit<reg::Trigger, 0>();
  }
  
  void set_output(uint32_t bit_set) {    
    if (bit_set == 0) {
      ctl.write<reg::Trigger>(0);
    } else{
      ctl.write<reg::Trigger>(2);
    }
  }
  
  void set_period(uint32_t period) {
    ctl.write<reg::Period>(period);
  }

  void set_Const_voltage(uint32_t Const_voltage) {
    ctl.write<reg::Const_voltage>(Const_voltage);
  }
  
  void set_Const_switch(uint32_t Const_switch) {
    ctl.write<reg::Const_switch>(Const_switch);
  }

  void set_acquisition_length(uint32_t acquisition_length) {
    ctl.write<reg::Acquisition_length>(acquisition_length);
  }
  
  void set_scale_LB(uint32_t scale_LB) {
    ctl.write<reg::Scale_LB>(scale_LB);
  }

 void set_lower_temp_lim(uint32_t lower_temp_lim) {
    ctl.write<reg::lower_temp_lim>(lower_temp_lim);
  }

 void set_upper_temp_lim(uint32_t upper_temp_lim) {
    ctl.write<reg::upper_temp_lim>(upper_temp_lim);
  }

  void set_scale_PC(uint32_t scale_PC) {
    ctl.write<reg::Scale_PC>(scale_PC);
  }
  
  void set_offset_LB(uint32_t offset_LB) {
    ctl.write<reg::Offset_LB>(offset_LB);
  } 

  void set_scale_Out(uint32_t scale_Out) {
    ctl.write<reg::Scale_Out>(scale_Out);
  }
  
  void set_offset_Out(uint32_t offset_Out) {
    ctl.write<reg::Offset_Out>(offset_Out);
  } 

  void set_offset_PC(uint32_t offset_PC) {
    ctl.write<reg::Offset_PC>(offset_PC);
  }
  
  uint32_t get_Temperature() {
    uint32_t temp_value = sts.read<reg::Temperature>();
    return temp_value;
  }

  uint32_t get_Volt_1() {
    uint32_t volt_1_value = sts.read<reg::Volt_1>();
    return volt_1_value;
  }

  uint32_t get_General_diagnostic() {
    uint32_t General_diagnostic_value = sts.read<reg::General_diagnostic>();
    return General_diagnostic_value;
  }


  uint32_t get_Volt_2() {
    uint32_t volt_2_value = sts.read<reg::Volt_2>();
    return volt_2_value;
  }

  uint32_t get_Isaturation() {
    uint32_t Isat_value = sts.read<reg::Isaturation>();
    return Isat_value;
  }
  
  uint32_t get_vFloat() {
    uint32_t vFloat_value = sts.read<reg::vFloat>();
    return vFloat_value;
  }
  
  uint32_t get_Timestamp() {
    uint32_t timestamp_value = sts.read<reg::Timestamp>();
    return timestamp_value;
  }
  
  //Adc FIFO
  
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
  
  void wait_for(uint32_t n_pts) {
    do {} while (get_fifo_length() < n_pts);
  }
  
  
  void start_fifo_acquisition();
  
  // Function to return the buffer length
  uint32_t get_buffer_length() {      
    return collected;
  }
  
  // Function to return data
  std::vector<uint32_t>& get_MLP_data() {
    
    // Will only return a valid array if data is available
    if (dataAvailable) {      
      dataAvailable = false;
      
      return adc_data;
      
    } else {
      return empty_vector;
    }
  }
  
  
private:
  Context& ctx;
  Memory<mem::control>& ctl;
  Memory<mem::status>& sts;
  Memory<mem::adc_fifo>& adc_fifo_map;
  
  std::vector<uint32_t> adc_data;
  std::vector<uint32_t> empty_vector;
  
  std::atomic<bool> fifo_acquisition_started{false};
  
  std::thread fifo_thread;
  // Member functions
  void fifo_acquisition_thread();
  uint32_t fill_buffer(uint32_t);
  // Member variables
  std::atomic<bool> dataAvailable{false};
  std::atomic<uint32_t> collected{0};         //number of currently collected data
};

inline void MLP::start_fifo_acquisition() {
  if (! fifo_acquisition_started) {
    fifo_thread = std::thread{&MLP::fifo_acquisition_thread, this};
    fifo_thread.detach();
  }
}

inline void MLP::fifo_acquisition_thread() {
  constexpr auto fifo_sleep_for = std::chrono::nanoseconds(5000);
  fifo_acquisition_started = true;
  ctx.log<INFO>("Starting fifo acquisition");
  adc_data.reserve(16777216);
  adc_data.resize(0);
  empty_vector.resize(0);
  
  uint32_t dropped=0;
  
  // While loop to reserve the number of samples needed to be collected
  while (fifo_acquisition_started){
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
    std::this_thread::sleep_for(fifo_sleep_for);
  }// While loop
}

// Member function to fill buffer array
inline uint32_t MLP::fill_buffer(uint32_t dropped) {
  // Retrieving the number of samples to collect
  uint32_t samples=get_fifo_length();
  
  // Collecting samples in buffer
  if (samples > 0) {
    // Checking for dropped samples
    if (samples >= 32768){  	
      dropped += 1;
    }
    // Assigning data to array
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

#endif // __DRIVERS_MLP_HPP__
