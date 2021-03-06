////////////////////////////////////////////////////////////////////////////////
// MOP5.cpp
//------------------------------------------------------------------------------

#include "spea2.hpp"
#include "spea2_io.hpp"
#include "island_model.hpp"

#include <fstream>
#include <iostream>
#include <cstdlib>


// genome: 2-dimensional genome data (2 variables per solution)
// ospace: three-dimensional objective space
void MOP5(const std::vector< float > &genome, std::vector< float> &ospace
	     , std::size_t population, std::size_t variables) 
{
    assert(ospace.size() == population * 3); 
    assert(genome.size() == population * variables); 

    for(std::size_t i=0; i < population; ++i) 
    {
	const float x = genome[i*variables + 0]; 
	const float y = genome[i*variables + 1];

	ospace[i*3 + 0] = .5f * (x*x + y*y) + std::sin(x*x + y*y); 
	ospace[i*3 + 1] = std::pow((3*x - 2*y + 4), 2.0f) / 8 
	    + std::pow((x-y+1), 2.0f) / 27 + 15; 
	ospace[i*3 + 2] = 1 / (x*x + y*y + 1) - 1.1f * std::exp(-(x*x) - (y*y)); 
    }
}

// returns true if the vector x is within our constraints
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

    // settings
    const std::size_t population = 500; 
    const std::size_t archive = 200; 
    const std::size_t generations = 200; 
    const std::size_t variables = 2; 
    const std::size_t max_crossover_attempts = 100; 
    const float       migration_prob = .05f;

    // variables must be within [-30, 30]
    std::vector< float > min_constraints(variables); 
    std::vector< float > max_constraints(variables); 
    fill(begin(min_constraints), end(min_constraints), -30.0f); 
    fill(begin(max_constraints), end(max_constraints), +30.0f); 

    // create a spea2 instance. this *could* be run without any mpi
    // involved: just call spea2.start() directly with exactly
    // the same arguments as island_model::start()
    libga_mpi::spea2< float > spea2(population, archive
        , min_constraints, max_constraints, 3); 

    // "wrap" the spea2 isntance in an island_model<> instance which knows
    // how to communicate via mpi. 
    libga_mpi::island_model< decltype(spea2) > im(spea2, migration_prob); 

    // note we call start() on the island model here and not on spea2 itself. 
    // if we want to run just a single-threaded optimization call spea2.start(). 
    const bool success 
	= im.start(
	    MOP5   // test function
	    , libga_mpi::xover::blxa<float>()   // crossover method
	    // algorithm returns if lambda returns true
	    , [generations](std::size_t g) { return g == generations; } 
	    // check a candidate solution (if it is within our constraints)
	    , [&](const float *x, std::size_t n) 
		{ return is_within_constraints(x, n, min_constraints, max_constraints); }
	    // mutation operator
	    , libga_mpi::mutation::mutate_none<float>()
	    // maximum number of crossover attempts for each new solution. 
	    // if no valid solution can be found after these attempts
	    // spea2::start() and island_model::start() return false. 
	    // the algorithm is said to have "stalled" then. 
	    , max_crossover_attempts); 
    
    if(success) 
    {
	// no errors occured, export data. 
	int rank;
	MPI_Comm_rank(MPI_COMM_WORLD, &rank); 
	// write a text file for forther processing
        std::ofstream stream("MOP5_data_" + std::to_string(rank)); 
	stream << spea2;
    }
    else
    {
	std::cout << "Algorithm stalled. Try increasing population "
		  << "or check constraints." << std::endl; 
	return 1; 
    }
    return 0; 
}
