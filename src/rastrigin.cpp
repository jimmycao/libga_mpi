////////////////////////////////////////////////////////////////////////////////
// rastrigin.cpp
//------------------------------------------------------------------------------

#include "sga.hpp"
#include "island_model.hpp"

#include <fstream>
#include <iostream>
#include <cstdlib>


static const float pi = 3.14159265358979323846f; 


void rastrigin(const std::vector< float > &genome, std::vector< float> &ospace
	     , std::size_t population, std::size_t variables) 
{
    for(std::size_t i=0; i < population; ++i) 
    {
	float obj = .0f;
	for(std::size_t j=0; j < variables; ++j) 
	{
	    const float x = genome[i*variables + j]; 
	    obj += x*x - 10*std::cos(2 * pi * x); 
	}
	ospace[i] = 10*variables + obj; 
    }
}

bool is_within_constraints(const float *x, std::size_t n
   , const std::vector< float > &min_c, const std::vector< float > &max_c) 
{
    for(std::size_t i=0; i < n; ++i) 
	if(x[i] < min_c[i] || x[i] > max_c[i]) 
	    return false; 
    return true; 
}


int main(int argc, char **argv) 
{
    MPI_Init(&argc, &argv); 
    atexit([]{ MPI_Finalize(); }); 

    const std::size_t population = 100; 
    const std::size_t generations = 200; 
    const std::size_t variables = 5; 
    const std::size_t max_crossover_attempts = 100; 
    const float       migration_prob = .2f;
    const float       elite_percentage = .3f;

    std::vector< float > min_constraints(variables); 
    std::vector< float > max_constraints(variables); 
    fill(begin(min_constraints), end(min_constraints), -5.12f); 
    fill(begin(max_constraints), end(max_constraints), +5.12f); 

    libga_mpi::sga< float > sga(population, elite_percentage
        , min_constraints, max_constraints); 
    libga_mpi::island_model< libga_mpi::sga< float >> im(sga, migration_prob); 

    const bool success 
	= sga.start(rastrigin, libga_mpi::xover::blxa<float>()
	      , [generations](std::size_t g) { return g == generations; }
		, [&](const float *x, std::size_t n) 
		{ return is_within_constraints(x, n
		       , min_constraints, max_constraints); }
		, libga_mpi::mutation::mutate_none<float>()
		, max_crossover_attempts); 
    
    if(success) 
    {
	int rank;
	MPI_Comm_rank(MPI_COMM_WORLD, &rank); 
	const std::size_t f = fittest(sga);
	std::ofstream stream("rastrigin_data_" + std::to_string(rank)); 
	for(std::size_t i=0; i < variables; ++i) 
	    stream << im.island().genome()[f*variables + i] << " "; 
	stream << im.island().ospace()[f]; 
    }
    else
    {
	std::cout << "Algorithm stalled. " << std::endl; 
	return 1; 
    }
    return 0; 
}
