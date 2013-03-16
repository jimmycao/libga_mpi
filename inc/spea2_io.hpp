////////////////////////////////////////////////////////////////////////////////
// spea2_io.hpp
//------------------------------------------------------------------------------


#pragma once

#include <ostream>

namespace libga_mpi 
{

template< typename T > class spea2; 

template< typename T >
std::ostream &operator << (std::ostream &os, const spea2< T > &alg) 
{
    const std::size_t population = alg.population(); 
    const std::size_t variables  = alg.variables(); 
    const std::size_t objectives = alg.objectives(); 

    const auto genome = alg.genome(); 
    const auto ospace = alg.ospace(); 
    const auto fitnesses = alg.fitnesses(); 

    for(std::size_t i=0; i < population; ++i) 
    {
	for(std::size_t j=0; j < variables; ++j) 
	    os << genome[i*variables + j] << " "; 
	for(std::size_t j=0; j < objectives; ++j) 
	    os << ospace[i*objectives + j] << " "; 
	os << fitnesses[i] << std::endl; 
    }

    return os; 
}


}
