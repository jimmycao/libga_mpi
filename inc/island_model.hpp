////////////////////////////////////////////////////////////////////////////////
// island_model.hpp
//------------------------------------------------------------------------------

#pragma once

#include <cstddef>
#include <vector>
#include <cassert>
#include <array>

#include "rand_source.hpp"
#include "topologies.hpp"
#include "mpi_util.hpp"


namespace libga_mpi 
{
namespace policies
{

template<   typename Island
	  , typename Topology
> 
class migrate_random 
{
public:
    using topology   = Topology; 
    using value_type = typename Island::value_type; 
    static_assert(std::is_floating_point< value_type >::value 
		  , "value_type must be a floating-point type"); 
public:
    migrate_random(const topology &topo, float prob) 
        : topo_{topo}, prob_{prob} 
    {
	assert(prob > 0); assert(prob < 1);
    }

    ~migrate_random() {}

    template< typename T >
    void operator () (const std::vector< T > &genome
        , const std::vector< T > &fitnesses
        , std::size_t population, std::size_t variables) 
    {
	const std::size_t emmigrants = static_cast< std::size_t >(
	    population * prob_); 
	for(std::size_t i=0; i < emmigrants; ++i) 
	{
	    const std::size_t x = static_cast< std::size_t >(rand_() * population); 
	    const std::size_t y = static_cast< std::size_t >(rand_() * population); 
	    const std::size_t emmi = fitnesses[x] < fitnesses[y] ? x : y; 

	    for(std::size_t dest : topo_.neighbors())
		mpi_util::send(&genome[emmi*variables], variables, dest); 
	}
    }

private:
    const topology &topo_; 
    float prob_;
    libga_mpi::detail::rand_source< value_type > rand_; 
}; 

template<   typename Island
	  , typename Topology
> 
class merge_random 
{
public:
    using topology   = Topology; 
    using value_type = typename Island::value_type; 
    static_assert(std::is_floating_point< value_type >::value 
		  , "value_type must be a floating-point type"); 
public:
    merge_random(const topology &topo, float prob) 
	: topo_{topo}, prob_{prob} 
    {
	assert(prob > 0); assert(prob < 1);
    }

    ~merge_random() {}

    template< typename T >
    void operator () (std::vector< T > &genome
	, std::size_t population, std::size_t variables)
    {
	const auto received = libga_mpi::mpi_util::receive< value_type >(variables);

	const std::size_t max_immigrants = static_cast< std::size_t >(
	    population * prob_); 
        const std::size_t accepted_immigrants = received.size() > max_immigrants 
	    ? max_immigrants : received.size(); 

	for(std::size_t i=0; i < accepted_immigrants; ++i) 
	{
	    const std::size_t rand_dest = static_cast< std::size_t >(
		population * rand_()); 
	    std::copy(begin(received[i]), end(received[i])
	      , &genome[rand_dest * variables]); 
	}
    }

private:
    const topology &topo_; 
    float prob_;
    libga_mpi::detail::rand_source< value_type > rand_; 
}; 

} // namespace policies


template<   
     typename Island 
   , typename Topology        = topologies::ring
   , typename MigrationPolicy = policies::migrate_random< Island, Topology  >
   , typename MergePolicy     = policies::merge_random<   Island, Topology  >
>
class island_model 
{
public: 
    using island_type      = Island; 
    using migration_policy = MigrationPolicy; 
    using merge_policy     = MergePolicy; 
    using topology         = Topology; 

public:
    island_model(island_type &island, float prob) 
	: island_{island}, prob_{prob}
    {
	assert(prob > 0); assert(prob < 1);
    }

    ~island_model() {}
    
    template<   typename EvalFn, typename QuitFn, typename XoverFn
	      , typename IsValidFn, typename MutateFn > 
    bool start( EvalFn eval_fn, XoverFn xover_fn
	      , QuitFn quit_fn, IsValidFn is_valid_fn, MutateFn mutate_fn
	      , std::size_t max_crossover_attempts)
    {
	const bool res = island_.start(eval_fn, xover_fn, quit_fn
	       , is_valid_fn, mutate_fn, max_crossover_attempts
	       , migration_policy(topology_, .1f), merge_policy(topology_, .1f)); 
	return res; 
    }

    const island_type &island() const { return island_; }

private:
    topology     topology_; 
    island_type &island_;
    float        prob_;
}; 


} // namespace libga_mpi 
