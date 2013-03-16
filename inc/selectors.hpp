////////////////////////////////////////////////////////////////////////////////
// selectors.hpp
//------------------------------------------------------------------------------


#pragma once

#include <cassert>
#include <cstddef>
#include <type_traits>
#include <vector>
#include <algorithm>
#include <numeric>

#include "rand_source.hpp"


namespace libga_mpi
{

namespace selectors
{

namespace detail 
{

template< typename It > 
inline void check_1d_integral_or_float_iterator(It os_it)
{
    using value_type = typename std::decay< decltype(*os_it) >::type; 
    static_assert(std::is_floating_point< value_type >::value 
      || std::is_integral< value_type >::value 
      , "It must be an iterator type to a floating-point or an "
      " integral type sequence. Usually this takes begin and end iterators "
      " to the SGA's one-dimensional objective space"); 
}

} // namespace detail 


template< typename T > 
class roulette_wheel_selector
{
public:
    static_assert(std::is_floating_point< T >::value 
		  , "T must be a floating-point type"); 
    using value_type = T; 

    roulette_wheel_selector() {}
    
    template< typename It > 
    roulette_wheel_selector(It fitnesses_begin, It fitnesses_end) 
    {
	detail::check_1d_integral_or_float_iterator(fitnesses_begin); 

	lh_.resize(distance(fitnesses_begin, fitnesses_end));  	
	partial_sum(fitnesses_begin, fitnesses_end, begin(lh_)); 
    }

    ~roulette_wheel_selector() {}

    std::size_t operator () () 
    {
	return distance(begin(lh_), lower_bound(begin(lh_), end(lh_), rand_())) - 1; 
    }

private:
    std::vector< value_type > lh_; 
    libga_mpi::detail::rand_source< value_type > rand_; 
}; 

template< typename T > 
class rank_selector
{
public:
    static_assert(std::is_floating_point< T >::value 
		  , "T must be a floating-point type"); 
    using value_type = T; 

    template< typename It > 
    rank_selector(It os_begin, It os_end)
    {
	detail::check_1d_integral_or_float_iterator(os_begin); 

	std::vector< std::size_t > seq(distance(os_begin, os_end));  
	std::size_t i=0; 
	generate(begin(seq), end(seq), [&i]{ return i++; }); 
	sort(begin(seq), end(seq), [&](std::size_t x, std::size_t y) 
	     { return *(os_begin + x) < *(os_begin + y); }); 
	rw_ = roulette_wheel_selector< value_type >(begin(seq), end(seq)); 
    }

    ~rank_selector() {}

    std::size_t operator () () { return rw_(); }

private:
    roulette_wheel_selector< value_type > rw_;
}; 


} // namespace libga_mpi::selectors
} // namespace libga_mpi 

