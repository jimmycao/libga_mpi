project(libga_mpi)
cmake_minimum_required(VERSION 2.6)

#add_definitions(-g -std=c++11 -Wall -pedantic)
add_definitions(-O3 -std=c++11 -Wall -pedantic)
find_package(MPI REQUIRED)

include_directories(${PROJECT_SOURCE_DIR}/inc)
include_directories(${MPI_INCLUDE_PATH})

# build the kursawe test problem
add_executable(kursawe ${PROJECT_SOURCE_DIR}/src/kursawe.cpp)
target_link_libraries(kursawe ${MPI_LIBRARIES})

# build rastrigin test problem
add_executable(rastrigin ${PROJECT_SOURCE_DIR}/src/rastrigin.cpp)
target_link_libraries(rastrigin ${MPI_LIBRARIES})

# build MOP5 test problem
add_executable(mop5 ${PROJECT_SOURCE_DIR}/src/MOP5.cpp)
target_link_libraries(mop5 ${MPI_LIBRARIES})