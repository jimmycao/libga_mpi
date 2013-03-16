////////////////////////////////////////////////////////////////////////////////
// spea2.cpp
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
#include "common.hpp"


namespace libga_mpi 
{

namespace detail 
{

template< typename Vec > 
inline auto sqdist(const Vec &v1, const Vec &v2, std::size_t n) 
    -> typename std::decay< decltype(v1[0]) >::type 
{
    using value_type = typename std::decay< decltype(v1[0]) >::type; 
    value_type ret = 0; 
    for(std::size_t i=0; i < n; ++i) 
    {
	const value_type d = v1[i] - v2[i]; 
	ret += d * d; 
    }
    return ret; 
}

template< typename Vec > 
inline void squared_distances(
    const Vec &in, Vec &out, std::size_t m, std::size_t n) 
{
    assert(in.size() == m * n); 
    assert(out.size() == m * m); 

    using value_type = typename std::decay< decltype(in[0]) >::type; 
    for(std::size_t i=0; i < m; ++i) 
    {
	out[i*m + i] = std::numeric_limits< value_type >::max(); 
	const float *in_i = &in[i*n]; 
	for(std::size_t j=0; j < i; ++j) 
	    out[i*m + j] = out[j*m + i] = sqdist(in_i, &in[j*n], n); 
    }
}

template< typename Vec > 
inline bool dominates(const Vec &v1, const Vec &v2, std::size_t n) 
{
    bool one_better = false; 
    for(std::size_t i=0; i < n; ++i) 
    {
	if(v1[i] > v2[i]) return false; 
	if(v1[i] < v2[i]) one_better = true; 
    }
    return one_better; 
}

template< typename Vec > 
inline std::size_t raw_strength(
    const Vec &ospace, std::size_t population, std::size_t objectives
    , std::size_t i)
{
    assert(ospace.size() == population * objectives); 
    assert(i < population); 

    std::size_t strength = 0; 
    for(std::size_t j=0; j < population; ++j) 
	if(i != j && dominates(&ospace[j*objectives], &ospace[i*objectives], objectives))
	    ++strength; 
    return strength; 
}

template< typename Vec > 
inline auto density_estimator(
    const Vec &ospace_sqdist, std::size_t population, std::size_t i)
    -> typename std::decay< decltype(ospace_sqdist[0]) >::type 
{
    assert(ospace_sqdist.size() == population * population); 
    assert(i < population); 

    const float *row = &ospace_sqdist[i*population]; 
    return 1 / (2 + std::sqrt(*std::min_element(row, row + population))); 
}

template< typename Vec > 
inline std::vector< std::size_t >::iterator truncation_pos(
    std::vector< std::size_t > &selection, const Vec &ospace_sqdist 
    , std::size_t population) 
{
    assert(selection.size() > 0); 
    assert(ospace_sqdist.size() == population * population); 

    using value_type = typename std::decay< decltype(ospace_sqdist[0]) >::type; 
    static_assert(std::is_floating_point< value_type >::value 
		  , "Vec must be a vector of floating-point elements"); 

    const std::size_t archive = selection.size(); 
    std::size_t min_index = 0; 
    value_type min_dist = std::numeric_limits< value_type >::max(); 

    for(std::size_t i=0; i < archive; ++i) 
    {
	const std::size_t s_i = selection[i]; 
	for(std::size_t j=0; j < i; ++j) 
	{
	    const value_type d = ospace_sqdist[s_i * population + selection[j]]; 
	    if(d < min_dist) 
	    {
		min_index = j; 
		min_dist = d; 
	    }
	}
    }
    return begin(selection) + min_index; 
}

template< typename Vec > 
inline void environmental_selection(
    const Vec &fitnesses, const Vec &ospace_sqdist
    , std::vector< std::size_t > &selection) 
{
    assert(fitnesses.size() * fitnesses.size() == ospace_sqdist.size()); 
    assert(selection.size() > 0); 

    const std::size_t population = fitnesses.size(); 
    const std::size_t archive    = selection.size(); 
    std::size_t visited = 0; 
    std::size_t filled  = 0; 

    for( ; visited < population && filled < archive; ++visited) 
	if(fitnesses[visited] < 1) 
	    selection[filled++] = visited; 
    for( ; visited < population; ++visited) 
	if(fitnesses[visited] < 1) 
	    *truncation_pos(selection, ospace_sqdist, population) = visited; 

    if(filled < archive) 
    {
	std::vector< std::size_t > dom; 
	for(visited = 0; visited < population; ++visited) 
	    if(fitnesses[visited] >= 1) 
		dom.push_back(visited); 

	partial_sort_copy(begin(dom), end(dom), begin(selection) + filled, end(selection)
		  , [&](std::size_t x, std::size_t y) 
		  { return fitnesses[x] < fitnesses[y] ? x : y; }); 
    }
}

template< typename Vec, typename Rand > 
std::size_t binary_tournament(const std::vector< std::size_t > &selection 
			      , const Vec &fitnesses, Rand &rand) 
{
    const std::size_t x = selection[
	static_cast< std::size_t >(selection.size() * rand())]; 
    const std::size_t y = selection[
	static_cast< std::size_t >(selection.size() * rand())]; 
    return fitnesses[x] < fitnesses[y] ? x : y; 
}


} // namespace detail


////////////////////////////////////////////////////////////////////////////////
// spea2
//------------------------------------------------------------------------------
template< typename T > 
class spea2
{
public: 
    using value_type = T; 
    static_assert(std::is_floating_point< T >::value 
		  , "T must be a floating-point type"); 

public:
    spea2(  std::size_t population, std::size_t archive 
	  , const std::vector< value_type > &min_constraints 
	  , const std::vector< value_type > &max_constraints
	  , std::size_t objectives) 
	: population_{population + archive}, archive_{archive}
	, variables_{min_constraints.size()}
	, objectives_{objectives}
	, min_constraints_{min_constraints}
	, max_constraints_{max_constraints}
    {
	genome_ = detail::random_genome(population_
    	     , min_constraints, max_constraints); 
	assert(objectives_ >= 2);
    }

    ~spea2() {}

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
	std::vector< value_type >  ospace_sqdist(population_ * population_); 
	std::vector< std::size_t > selection(archive_); 

	fitnesses_.resize(population_); 
	ospace_.resize((population_) * objectives_); 

	for(std::size_t generation = 0 ;; ++generation) 
	{
	    eval_fn(genome_, ospace_, population_, variables_); 

	    detail::squared_distances(ospace_, ospace_sqdist
	        , population_, objectives_); 
	    this->assign_fitnesses(ospace_sqdist);

	    if(quit_fn(generation))
		return true; 

	    migrate_fn(genome_, fitnesses_, population_, variables_);

	    detail::environmental_selection(fitnesses_, ospace_sqdist, selection); 

	    if(false == this->crossover(next_genome, selection
	        , xover_fn, is_valid_fn, mutate_fn, max_crossover_attempts))
	        return false;

	    this->copy_archive(next_genome, selection);
	    merge_fn(next_genome, population_, variables_);
	    swap(next_genome, genome_); 
	}
    }

    const std::vector< value_type > &genome() const { return genome_; }
    const std::vector< value_type > &ospace() const { return ospace_; }
    const std::vector< value_type > &fitnesses() const { return fitnesses_; }
    std::size_t population() const { return population_; }
    std::size_t variables()  const { return variables_; }
    std::size_t objectives() const { return objectives_; }

private: 
    std::size_t population_, archive_, variables_, objectives_; 
    std::vector< value_type > genome_, ospace_, fitnesses_
	, min_constraints_, max_constraints_; 

private: 
    template< typename XoverFn, typename IsValidFn, typename MutateFn > 
    bool crossover(std::vector< value_type > &next_genome 
		   , const std::vector< std::size_t > &selection
		   , XoverFn xover_fn, IsValidFn is_valid_fn, MutateFn mutate_fn
		   , std::size_t max_attempts)
    {
	assert(genome_.size() == next_genome.size()); 
	assert(selection.size() == archive_); 

	detail::rand_source< value_type > rand; 

	for(std::size_t i=0; i < population_ - archive_; ++i) 
	{
	    for(std::size_t attempt = 0 ;; ++attempt) 
	    {
		const std::size_t x = detail::binary_tournament(
		    selection, fitnesses_, rand); 
		const std::size_t y = detail::binary_tournament(
		    selection, fitnesses_, rand); 

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
	return true; 
    }

    void assign_fitnesses(const std::vector< value_type > &ospace_sqdist)
    {
	assert(ospace_sqdist.size() == population_ * population_); 

	for(std::size_t i=0; i < population_; ++i) 
	    fitnesses_[i] = detail::raw_strength(ospace_, population_, objectives_, i) 
		+ detail::density_estimator(ospace_sqdist, population_, i); 
    }

    void copy_archive(std::vector< value_type >&next_genome
		      , const std::vector< std::size_t > &selection) 
    {
	assert(next_genome.size() == genome_.size()); 
	assert(selection.size() == archive_); 

	for(std::size_t i=0; i < archive_; ++i)
	{
	     const float *src = &genome_[selection[i] * variables_]; 
	     float *dest = &next_genome[(population_ - archive_ + i) * variables_]; 
	     std::copy(src, src + variables_, dest); 
	}
    }
}; 


} // namespace libga_mpi
