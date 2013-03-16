////////////////////////////////////////////////////////////////////////////////
// sga.cpp
//------------------------------------------------------------------------------

#pragma once 

#include <cassert>
#include <type_traits>
#include <cstddef>
#include <algorithm>
#include <vector>

#include "rand_source.hpp"
#include "xover.hpp"
#include "mutation.hpp"
#include "selectors.hpp"
#include "common.hpp"


namespace libga_mpi
{


////////////////////////////////////////////////////////////////////////////////
// sga
//------------------------------------------------------------------------------
template< typename T
	  , typename Selector = selectors::rank_selector< T >
> 
class sga
{
public: 
    using value_type = T; 
    using selector_type = Selector; 

    static_assert(std::is_floating_point< T >::value 
		  , "T must be a floating-point type"); 

public:
    sga(  std::size_t population, value_type elite_percentage
	  , const std::vector< value_type > &min_constraints 
	  , const std::vector< value_type > &max_constraints
	  )
	: elite_percentage_{elite_percentage}
	, population_{population}
	, variables_{min_constraints.size()}
	, min_constraints_{min_constraints}
	, max_constraints_{max_constraints}
    {
	assert(elite_percentage >= 0); assert(elite_percentage < 1); 
	genome_ = libga_mpi::detail::random_genome(population_
    	     , min_constraints, max_constraints); 
    }

    ~sga() {}

    template<   typename EvalFn, typename QuitFn, typename XoverFn
	      , typename IsValidFn, typename MutateFn 
	      , typename MigrateFn = no_island_model_context::migrate_none
	      , typename MergeFn   = no_island_model_context::merge_none > 
    bool start( EvalFn eval_fn, XoverFn xover_fn
	      , QuitFn quit_fn, IsValidFn is_valid_fn, MutateFn mutate_fn
	      , std::size_t max_crossover_attempts
	      , MigrateFn migrate_fn = no_island_model_context::migrate_none() 
	      , MergeFn merge_fn = no_island_model_context::merge_none() )
    {
	std::vector< value_type >  next_genome(population_ * variables_); 
	ospace_.resize(population_); 

	for(std::size_t generation = 0 ;; ++generation) 
	{
	    eval_fn(genome_, ospace_, population_, variables_); 
	    
	    if(quit_fn(generation))
		return true;
	    
	    migrate_fn(genome_, ospace_, population_, variables_); 

	    if(false == this->crossover(next_genome, xover_fn, is_valid_fn
		, mutate_fn, max_crossover_attempts))
		return false;

	    merge_fn(next_genome, population_, variables_); 
	    swap(next_genome, genome_); 
	}
    }

    const std::vector< value_type > &genome() const { return genome_; }
    const std::vector< value_type > &ospace() const { return ospace_; }
    std::size_t population() const { return population_; }
    std::size_t variables()  const { return variables_; }
    std::size_t objectives() const { return 1; }

private: 
    value_type elite_percentage_;
    std::size_t population_, variables_; 
    std::vector< value_type > genome_, ospace_, min_constraints_, max_constraints_; 

private:
    template< typename XoverFn, typename IsValidFn, typename MutateFn > 
    bool crossover(std::vector< value_type > &next_genome
		   , XoverFn xover_fn, IsValidFn is_valid_fn
		   , MutateFn mutate_fn, std::size_t max_attempts) 
    {
	assert(genome_.size() == next_genome.size()); 
	
	libga_mpi::detail::rand_source< value_type > rand; 
	const std::size_t elite = static_cast< std::size_t >(
	    population_ * elite_percentage_); 

	selector_type select(begin(ospace_), end(ospace_)); 

	for(std::size_t i=0; i < population_ - elite; ++i)
	{
	    for(std::size_t attempt = 0 ;; ++attempt) 
	    {
		const std::size_t x = select(); 
		const std::size_t y = select(); 

		xover_fn(&genome_[x*variables_], &genome_[y*variables_]
			 , &next_genome[i*variables_], variables_); 

		if(is_valid_fn(&next_genome[i*variables_], variables_))
		{
		    mutate_fn(&next_genome[i*variables_], variables_); 
		    break; 
		}
		if(max_attempts > 0 && attempt == max_attempts) 
		    return false; 
	    }
	}

	// propagate elite
	if(elite > 0) 
	{
	    std::vector< std::size_t > seq(population_); 
	    std::vector< std::size_t > elite_indices(elite); 
	    std::size_t i=0; 
	    generate(begin(seq), end(seq), [&i]{ return i++; }); 

	    partial_sort_copy(begin(seq), end(seq), begin(elite_indices), end(elite_indices)
		  , [&](std::size_t x, std::size_t y) 
		  { return ospace_[x] < ospace_[y]; }); 
	    for(std::size_t i=0; i < elite; ++i)
	    {
		const float *src = &genome_[elite_indices[i] * variables_]; 
		float *dest = &next_genome[(population_ - elite + i) * variables_]; 
		std::copy(src, src + variables_, dest); 
	    }
	}
	return true; 
    }
};

template< typename T, typename Selector > 
inline std::size_t fittest(const sga< T, Selector > &s)
{
    return distance(begin(s.ospace()), min_element(begin(s.ospace()), end(s.ospace()))); 
}


} // namespace libga_mpi
