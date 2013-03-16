#pragma once

#include <cstddef>
#include <cassert>
#include <type_traits>

#include "rand_source.hpp"

namespace libga_mpi
{
namespace mutation
{

template< typename T > 
struct mutate_none 
{
    template< typename It > 
    void operator () (It v, std::size_t) {}
}; 

template< typename T > 
struct mutate_uniform
{
    static_assert(std::is_floating_point< T >::value 
		  , "T must be a floating-point type"); 
    T prob_; 
    std::vector< T > min_constraints_, max_constraints_; 
    libga_mpi::detail::rand_source< T > rand_; 

    mutate_uniform(T prob, const std::vector< T > &min_constraints
		   , const std::vector< T > &max_constraints)
	: prob_{prob}, min_constraints_{min_constraints}
	, max_constraints_{max_constraints}
    {}
    ~mutate_uniform() {}

    template< typename It > 
    void operator () (It v, std::size_t n) 
    {
	for(std::size_t i=0; i < n; ++i) 
	{
	    if(rand_() <= prob_)
		v[i] = min_constraints_[i]+(max_constraints_[i]
		   -min_constraints_[i]) * rand_(); 
	}
    }
}; 

} // namespace mutation
} // namespace libga_mpi
