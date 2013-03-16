////////////////////////////////////////////////////////////////////////////////
// xover.hpp
//------------------------------------------------------------------------------


#pragma once

#include <cassert>
#include <type_traits>
#include <cmath>
#include <cstddef>

#include "rand_source.hpp"


namespace libga_mpi
{

namespace xover
{

template< typename T > 
struct sbx
{
    static_assert(std::is_floating_point< T >::value 
		  , "T must be a floating-point type"); 
    static constexpr T mu = static_cast< T >(2.0f); 
    libga_mpi::detail::rand_source< T > rand_; 

    template< typename It > 
    void operator () (const It p1, const It p2, It c, std::size_t n) 
    {
	const T R = rand_(); 
	T b = R < .5f
	    ? std::pow(2*R, 1/(mu+1)) : std::pow(1/(2*(1-R)), 1/(mu+1)); 
	if(rand_() <= .5f)
	    b = -b; 
	for(std::size_t i=0; i < n; ++i) 
	    c[i] = ((1+b)*p1[i] + (1-b)*p2[i]) / 2; 
    }
}; 

template< typename T > 
struct blxa
{
    static_assert(std::is_floating_point< T >::value 
		  , "T must be a floating-point type"); 
    static constexpr T alpha = static_cast< T >(.5f);
    libga_mpi::detail::rand_source< T > rand_; 

    template< typename It > 
    void operator () (const It p1, const It p2, It c, std::size_t n) 
    {
	for(std::size_t i=0; i < n; ++i) 
	{
	    T low  = p1[i]; 
	    T high = p2[i]; 
	    if(high < low) 
		std::swap(low, high); 
	    const T I = (high - low) * blxa::alpha; 
	    const T R = rand_(); 
	    c[i] = 2*I*R - I + high*R - low*R + low; 
	}
    }
}; 


} // namespace xover
} // namespace libga_mpi
