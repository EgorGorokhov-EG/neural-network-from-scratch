import numpy as np


class NeuralNet:
    """
    Implements simple neural net

    Arguments:
    n -- list of dimensions for each layer
    lr -- learning rate for gradient descent
    num_iterations -- number of iterations of optimization loop
    print_cost -- if True, prints cost for every 100 steps
    """

    def __init__(self, n, lr=0.0075, num_iterations=3000, print_cost=False):

        self.n = n
        self.lr = lr
        self.num_iterations = num_iterations
        self.print_cost = print_cost
        self.trained_params = {}
        self.fitted = False

    def cost_function(self, Y_true, Y_pred):
        """
        Arguments:
        Y_true -- vector of true labels for training set, shape(1, number of examples)
        Y_pred -- probability vector corresponding to label predictions, shape(1, number of examples)

        Returns:
        cost -- cross entropy cost
        """
        m = Y_true.shape[1]  # number of examples
        J = -(1 / m) * np.sum(Y_true * np.log(Y_pred) + (1 - Y_true) * np.log(1 - Y_pred))
        return J

    def init_params(self, n):
        """
        Creating random weigths and biases for all layers in NN

        Arguments:
        n -- array of numbers of units in each layer

        Returns:
        params -- dictionary of weights and biases for each layer of NN:
                  Wl -- weigths matrix of l-th layer, shape(n[l], n[l-1])
                  bl -- bias vector of l-th layer, shape(n[l], 1)
        """

        params = {}
        L = len(n)  # number of layers in NN

        for l in np.arange(1, L):
            params['W' + str(l)] = np.random.randn(n[l], n[l - 1]) * 0.01  # multiplying all values to train NN faster
            params['b' + str(l)] = np.zeros((n[l], 1))

        return params

    def L_model_forward(self, X, parameters):
        """
        Implements forward propagation part of L layer Neural Net
        Arguments:
        X -- input data
        parameters -- dictionary with weights and biases for every layer

        Returns:
        AL -- activations from the last layer
        caches -- linear caches for every layer
        """

        def relu(Z):
            """ReLU function"""
            return max(0, Z)

        def sigmoid(Z):
            """Sigmoid function"""
            return 1 / (1 + np.exp(Z))

        def linear_forward(A_prev, W, b):
            """
            Linear part of forward propagation.

            Arguments:
            A_prev -- activations from previous layer or input(X)
            W -- weights for current layer
            b -- biases for current layer

            Returns:
            Z -- the input for the activation function
            cache -- dictionary containing A_prev, W and b

            """

            Z = np.dot(W, A_prev) + b
            cache = A_prev, W, b

            return Z, cache

        def activation_forward(A_prev, W, b, activation):
            """
            Forward propagation for activation part of layer

            Arguments:
            A_prev -- activations from previous layer or input(X)
            W -- weights for current layer
            b -- biases for current layer
            activtion -- activation function to use in this layer

            Returns:
            A -- activations from this layer
            cache -- tuple containing values of A_prev and calculated in this layer W, b, Z
            """

            Z, linear_cache = linear_forward(A_prev, W, b)

            if activation == 'ReLU':
                vec_relu = np.vectorize(relu)
                A = vec_relu(Z)
            elif activation == 'Sigmoid':
                A = sigmoid(Z)

            cache = (linear_cache, Z)

            return A, cache

        caches = []
        A = X

        L = len(parameters) // 2

        for l in range(1, L):
            A_prev = A
            A, cahce = activation_forward(A_prev, parameters['W' + str(l)], parameters['b' + str(l)], 'ReLU')
            caches.append(cache)

        AL, cache = activation_forward(A, parameters['W' + str(L)], parameters['b' + str(L)], 'Sigmoid')
        caches.append(cache)

        return AL, caches

    def L_model_backward(self, AL, Y, caches):
        """
        Implements backward propagation part of L layer Neural Net
        Arguments:
        AL -- activation of the last layer
        Y -- true labels for data X
        caches -- list of caches for every layer

        Returns:
        grads -- A dictionary with the gradients
                 grads["dA" + str(l)] = ...
                 grads["dW" + str(l)] = ...
                 grads["db" + str(l)] = ...
        """

        def sigmoid(Z):
            """Sigmoid function"""
            return 1 / (1 + np.exp(Z))

        def relu_backward(dA, Z):

            def relu_derivative(Z):
                if Z < 0:
                    return 0
                elif Z >= 0:
                    return 1

            dZ = np.multiply(dA, np.vectorize(relu_derivative(Z)))
            return dZ

        def sigmoid_backward(dA, Z):

            def sigmoid_derivative(Z):
                return np.multiply(sigmoid(Z), (1 - sigmoid(Z)))

            dZ = np.multiply(dA, sigmoid_derivative(Z))
            return dZ

        def linear_back(dZ, cache):
            """
            Back propagation for linear section of layer

            Arguments:
            dZ -- Gradient of the cost function w.r.t linear output of current layer
            cache -- tuple of A_prev, W, b values used in this layer

            Returns:
            dA_prev -- Gradient of the co w.r.t activations fom previous layer
            dW -- Gradient of the cost w.r.t weights
            db -- Gradient of the cost w.r.t biases
            """

            A_prev, W, b = cache
            m = a_prev.shape[1]

            dW = np.dot(dZ, A_prev.T) / m
            db = np.sum(dZ, axis=1, keepdims=True) / m
            dA_prev = np.dot(W.T, dZ)

            return dA_prev, dW, db

        def activation_back(dA, cache, activation):
            """
            Back propagation for the activation part of the current layer

            Arguments:
            dA -- Gradient wrt activations of the current layer
            cache -- A_prev, W, b, Z for current layer
            activation -- activation function to use in this layer

            Returns:
            dA_prev -- Gradient of the cost wrt the activation of the previous layer
            dW -- Gradient of the cost wrt W (current layer l), same shape as W
            db -- Gradient of the cost wrt b (current layer l), same shape as b
            """

            linear_cache, Z = cache

            if activation == 'ReLu':
                dZ = relu_backward(dA, Z)
            if activation == 'Sigmoid':
                dZ = sigmoid_backward(dA, Z)

            dA_prev, dW, db = linear_back(dZ, linear_cache)

            return dA_prev, dW, db

        grads = {}
        L = len(cahces)
        Y = Y.reshape(AL.shape)
        m = AL.shape[1]

        dAL = -(np.divide(Y, AL) - np.divide(1 - Y, 1 - AL))

        grads['dA' + str(L)], grads['dW' + str(L)], grads['db' + str(L)] = activation_back(dAL,
                                                                                           caches[-1],
                                                                                           'Sigmoid')

        for l in reversed(range(1, L)):
            grads['dA' + str(l)], grads['dW' + str(l)], grads['db' + str(l)] = activation_back(grads['dA' + str(l + 1)],
                                                                                               caches[l])

        return grads

    def update_params(self, parameters, grads, lr):
        """
        Updates parameters using gradient descent
        Arguments:
        parameters -- dictionary with parameters for every layer
        grads -- dictionary with gradients for every layer
        lr -- learning rate for gradient descent

        Returns:
        parameters -- dictionary of updated parameters
        """

        L = len(parameters) // 2

        for l in range(L):
            parameters['W' + str(l + 1)] -= grads['dW' + str(l + 1)] * lr
            parameters['b' + str(l + 1)] -= grads['db' + str(l + 1)] * lr

        return parameters

    def fit(self, X_train, Y_train):
        """
        Trains the NN for classification
        Arguments:
        X_train -- train data
        Y_train -- true labels for train data
        """

        self.fitted = True

        parameters = self.init_params(self.n)

        for i in range(self.num_iterations):

            AL, caches = self.L_model_forward(X_train, parameters)
            cost = self.cost_function(Y_train, AL)
            grads = self.L_model_backward(AL, Y_train, caches)
            parameters = self.update_params(parameters, grads, self.lr)

            if self.print_cost and (i % 100 == 0):
                print(cost)
                costs.append(cost)

        self.trained_params = parameters

    def predict(self, X_test):
        """
        Predicts labels for X_test data
        """

        if self.fitted:
            Y, caches = self.L_model_forward(X_test, self.trained_params)
        else:
            print("Error: The Neural Network isn't fitted yet. Call .fit() method first")

        return Y