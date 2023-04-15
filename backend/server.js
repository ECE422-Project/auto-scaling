'use strict'


const fastify = require('fastify')();


fastify
    .register(require('@fastify/redis'), { 
        host: '10.2.6.145', 
        port: 6379, // Redis port
        family: 4   // 4 (IPv4) or 6 (IPv6)
    })
    .register(require('@fastify/cors'), {
        origin: [ 'http://10.2.6.145:5173' ],
        method: [ 'GET' ],
    });


fastify.get('/avg_response_time', (req, reply) => {
    const { redis } = fastify;

    redis.get('avg_response_time', (err, val) => {
        if (err) {
            reply.send(err);
        } else {
            reply.send(val || 0);
        }
    });
});

fastify.get('/replicas', (req, reply) => {
    const { redis } = fastify;

    redis.get('num_replications', (err, val) => {
        if (err) {
            reply.send(err);
        } else {
            reply.send(val || 0);
        }
    });
});

fastify.get('/workload', (req, reply) => {
    const { redis } = fastify;

    redis.get('workload', (err, val) => {
        if (err) {
            reply.send(err);
        } else {
            reply.send(val || 0);
        }
    });
});

fastify.listen({ host: '0.0.0.0', port: 9000 }, err => {
    if (err) {
        throw err;
    }

    console.log(`server listening on ${fastify.server.address().port}`);
});
