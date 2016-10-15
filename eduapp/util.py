from __future__ import print_function

import json
from django.http import HttpResponse
import tensorflow as tf
import numpy
rng = numpy.random

import matplotlib.pyplot as plt

learning_rate = 0.01
training_epochs = 1000
display_step = 50

x_value_factor = 0.0001

def get_training(data):
    training_x = numpy.asarray([(float(d.totalRev()) / d.pop) * x_value_factor for d in data])
    training_y = numpy.asarray([d.getPerformanceMetric() for d in data])
    return training_x, training_y

def json_response(data):
    return HttpResponse(json.dumps(data), content_type='application/json')

class MachineLearningModel:
    def __init__(self, W, b):
        self.W = W
        self.b = b
    def calculate(self, x):
        return x * self.W + self.b

def get_model(training_x, training_y):
    X = tf.placeholder("float")
    Y = tf.placeholder("float")

    W = tf.Variable(rng.randn(), name="weight")
    b = tf.Variable(rng.randn(), name="bias")

    n_samples = training_x.shape[0]

    pred = tf.add(tf.mul(X, W), b)

    cost = tf.reduce_sum(tf.pow(pred-Y, 2))/(2*n_samples)


    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

    init = tf.initialize_all_variables()


    s = tf.Session()
    s.run(init)


    for epoch in range(training_epochs):
        for (x,y) in zip(training_x, training_y):
            s.run(optimizer, feed_dict={X: x, Y: y})

        if (epoch + 1) % display_step == 0:
            c = s.run(cost, feed_dict={X: training_x, Y:training_y})
            print("Iteration:", '%04d' % (epoch+1), "Cost:", "{:.9f}".format(c), "m:", s.run(W), "b:", s.run(b))


    print("Optimization finished!")
    training_cost = s.run(cost, feed_dict={X: training_x, Y:training_y})



    return MachineLearningModel(s.run(W), s.run(b))
