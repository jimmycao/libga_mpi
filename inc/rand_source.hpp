////////////////////////////////////////////////////////////////////////////////
// rand_source.hpp
//------------------------------------------------------------------------------


#pragma once

#include <cassert>
#include <type_traits>
#include <random>
#include <ctime>


namespace libga_mpi 
{
namespace detail
{

template< typename T > 
class rand_source
{
public:
    static_assert(std::is_floating_point< T >::value 
		  , "T must be a floating-point element"); 
    using value_type = T;
    rand_source() { mt_.seed(static_cast<unsigned int>(std::time(nullptr))); }
    ~rand_source() {}
    value_type operator () () { return dist_(mt_); }

private:
    std::mt19937 mt_; 
    std::uniform_real_distribution< value_type > dist_; 
};



}
}
