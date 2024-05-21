#!/bin/bash


echo "Killing any existing microservices to avoid port conflicts..."

# Example of killing by port number
# shellcheck disable=SC2046
kill $(lsof -t -i:5555) 2>/dev/null
# shellcheck disable=SC2046
kill $(lsof -t -i:5556) 2>/dev/null
# shellcheck disable=SC2046
kill $(lsof -t -i:5557) 2>/dev/null
# shellcheck disable=SC2046
kill $(lsof -t -i:5558) 2>/dev/null
# shellcheck disable=SC2046
kill $(lsof -t -i:5560) 2>/dev/null


echo "Checking for logs directory..."
if [ ! -d "logs" ]; then
  mkdir -p logs
  echo "Created logs directory."
fi


echo "Starting all microservices..."

# Start Microservice A
# shellcheck disable=SC2188
node ../../CS361/text-tp-microservice.git/server.js > logs/A.log 2>&1 &
echo "Microservice A started..."

# Start Microservice B
python3 breaks_service.py > logs/B.log 2>&1 &
echo "Microservice B started..."

# Start Microservice C
python3 setting_service.py > logs/C.log 2>&1 &
echo "Microservice C started..."

# Start Microservice D
python3 task_service.py > logs/D.log 2>&1 &
echo "Microservice D started..."

# Start Microservice E
python3 timer_service.py > logs/E.log 2>&1 &
echo "Microservice E started..."

echo "All microservices are running in the background."


# make exe
# chmod +x start_microservices.sh

# kill pids
#lsof -i :5556
# kill -9 5556