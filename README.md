# auto-scaling
ECE 422 Reliability Project

This is a reactive auto-scaling engine based in Python for a cloud
microservice application. The application is meant to be deployed onto the Cybera
Rapid Access Cloud infrastructure using Docker microservices. It also includes a
webpage for the real-time plot of some of its response and scalability metrics.


It uses horizontal scalability to adjust the application based on user workload. The auto-scaler
will monitor response times and adjust the number of microservice instances to maintain
an acceptable range of response times, defined by upper and lower thresholds. If
response times exceed the upper threshold, the auto-scaler will scale out the
application to ensure reliability and performance. Conversely, if response times fall
below the lower threshold, the auto-scaler will scale in the application to optimize
operational costs on the cloud. By implementing this self-adaptive application, we aim to
achieve optimal performance and cost-effectiveness simultaneously.
