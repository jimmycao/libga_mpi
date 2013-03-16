#pragma once

#include <cstddef>
#include <vector>
#include <string>
#include <stdexcept>

#include <mpi.h>


namespace libga_mpi
{
namespace mpi_util
{

int mpi_data_type(float) { return MPI_FLOAT; }
int mpi_data_type(double) { return MPI_DOUBLE; }

template< typename It > 
inline void send(const It v, std::size_t len, std::size_t dest)
{
    using value_type = typename std::decay< decltype(*v) >::type; 
    static_assert(std::is_floating_point< value_type >::value 
		  , "It must be an iterator into a floating-point array"); 

    void *ptr = static_cast< void *>(const_cast< value_type *>(v)); 
    const int err = MPI_Send(ptr, len, mpi_data_type(value_type())
	     , dest, 0, MPI_COMM_WORLD);
    if(err != MPI_SUCCESS)
    {
	throw std::runtime_error("MPI Error while sending a solution "
	 " of length " + std::to_string(len));
    }
}

template< typename T > 
inline std::vector<std::vector< T >> receive(std::size_t len) 
{
    using value_type = T;
    static_assert(std::is_floating_point< value_type >::value 
		  , "T must be a floating-point type"); 
    std::vector<std::vector< value_type >> rec; 

    int flag = static_cast< int >(true);
    MPI_Status status;

    MPI_Iprobe(MPI_ANY_SOURCE, MPI_ANY_TAG
	    , MPI_COMM_WORLD, &flag, &status); 
    while(flag)
    {
	int count = 0;
	MPI_Get_count(&status, mpi_data_type(value_type()), &count); 
	std::vector< T > vec(count);
	void *ptr = static_cast< void *>(const_cast< value_type *>(&vec[0])); 

	const int err = MPI_Recv(ptr, count, mpi_data_type(value_type())
	    , status.MPI_SOURCE, status.MPI_TAG, MPI_COMM_WORLD, &status); 
	if(err != MPI_SUCCESS)
	{
	    throw std::runtime_error("MPI Error while receiving solution "
	     " of length " + std::to_string(count)); 
	}
	if(count == len)
	{
	    // we have received a complete solution vector
            rec.push_back(vec);
	}
	MPI_Iprobe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &flag, &status);
    }
    return rec;
}

} // namespace mpi_util 
} // namespace libga_mpi
