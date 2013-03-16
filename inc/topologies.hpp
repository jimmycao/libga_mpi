////////////////////////////////////////////////////////////////////////////////
// topologies.hpp
//------------------------------------------------------------------------------


#pragma once

#include <cstddef>
#include <array>
#include <stdexcept> 

#include <mpi.h>


namespace libga_mpi
{
namespace topologies
{

class ring
{
public:
    ring() 
    {
	MPI_Comm_rank(MPI_COMM_WORLD, &rank_); 
	MPI_Comm_size(MPI_COMM_WORLD, &size_); 
	if(size_ < 3)
	{
	    throw std::runtime_error("The ring topology is only supported "
            "for three and more nodes"); 
	}
	neighbors_[0] = rank_ < size_ - 1 ? rank_ + 1 : 0; 
	neighbors_[1] = rank_ > 0 ? rank_ - 1 : size_ - 1;
    }

    ~ring() {}

    const std::array< std::size_t, 2 > &neighbors() const { return neighbors_; }

    int size() const { return size_; }

private:
    std::array< std::size_t, 2 > neighbors_; 
    int rank_, size_; 
}; 

} // namespace topologies
} // namespace libga_mpi
