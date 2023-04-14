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


fastify.get('/status', function (req, reply) {
    const { redis } = fastify;

    redis.mget(
        'avg_response_time', 'num_replications', 'num_visitors', 
        (err, vals) => {
            if (err) {
                reply.send(err);
            } else {
                const data = [];
                vals.forEach(val => data.push(val || 0));
                reply.send(data);
            }
        }
    );
});


fastify.listen({ host: '0.0.0.0', port: 3000 }, err => {
    if (err) {
        throw err;
    }

    console.log(`server listening on ${fastify.server.address().port}`);
});
