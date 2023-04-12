'user strict'

const fastify = require('fastify')();

fastify.register(require('@fastify/redis'), {
    host: '10.2.6.145',
    port: 6379,
    family: 4
});

fastify.register(require('@fastify/cors'), {
    origin: "*",
    methods: ["GET"],
});


fastify.get('/query', function (req, reply) {
    const { redis } = fastify;

    redis.get(req.query.key, (err, val) => {
        console.log(val);

        reply.send(err || val);
    });
});


fastify.listen({ host: '0.0.0.0', port: 3000 }, err => {
    if (err) {
        throw err;
    }

    console.log(`server listening on ${fastify.server.address().port}`);
});
