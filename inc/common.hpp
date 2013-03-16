////////////////////////////////////////////////////////////////////////////////
// common.hpp
//------------------------------------------------------------------------------

#pragma once

#include <cstddef>
#include <vector>

#include "rand_source.hpp"


namespace libga_mpi 
{

namespace no_island_model_context
{

struct migrate_none 
{
    template< typename T >
    void operator () (
        const std::vector< T >&, const std::vector< T >&
      , std::size_t, std::size_t) 
    {}
}; 

struct merge_none  
{
    template< typename T >
    void operator () (
	const std::vector< T >&, std::size_t, std::size_t)
    {}
}; 

} // namespace no_island_model_context

namespace detail 
{

template< typename Vec >
inline Vec random_genome(std::size_t population 
   , const Vec &min_constraints, const Vec &max_constraints) 
{
    assert(population > 0); 
    assert(min_constraints.size() == max_constraints.size()); 

    using value_type = typename std::decay< decltype(min_constraints[0]) >::type; 
    static_assert(std::is_floating_point< value_type >::value 
		  , "Vec must be a vector of floating-point elements"); 

    const std::size_t variables = min_constraints.size(); 
    Vec genome(population * variables); 
    libga_mpi::detail::rand_source< value_type > rand; 

    for(std::size_t i=0; i < population; ++i) 
    {
	for(std::size_t j=0; j < variables; ++j)
	    genome[i*variables + j] = min_constraints[j]
		+ (max_constraints[j]-min_constraints[j]) * rand(); 
    }
    return genome; 
}


} // namespace detail
} // namespace libga_mpi
