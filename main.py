import argparse

import numpy as np
from matplotlib import pyplot as plt
from src.data import load_data
from src.methods.dummy_methods import DummyClassifier
from src.methods.logistic_regression import LogisticRegression
from src.methods.linear_regression import LinearRegression 
from src.methods.knn import KNN
from src.utils import normalize_fn, append_bias_term, accuracy_fn, macrof1_fn, mse_fn, compute_mean, compute_std, create_validation_set,run_cv_for_hyperparam
import os
np.random.seed(100)

def evaluate_knn_on_validation_set(X_train, Y_train, X_val, Y_val, k):

    '''

    Trains and evaluates a KNN model on the provided training and validation sets.

    Parameters:

    - X_train: Feature matrix for the training data.

    - Y_train: Labels for the training data.

    - X_val: Feature matrix for the validation data.

    - Y_val: Labels for the validation data.

    - k: The number of neighbors to use in the KNN model.

    Returns:
    - accuracy: The accuracy of the KNN model on the validation set.

    '''

    # Instantiate the KNN model with the specified 'k'

    knn_model = KNN(k)

    # Train the KNN model on the training set
    knn_model.fit(X_train, Y_train)

    # Make predictions on the validation set
    Y_val_pred = knn_model.predict(X_val)

    # Calculate the accuracy of the predictions
    accuracy = accuracy_fn(Y_val_pred, Y_val)

    return accuracy



def plot_k_vs_accuracy_cv(k_list, model_performance):

    plt.figure(figsize=(9,4))

    plt.plot(k_list, model_performance, marker='o')

    plt.title("Performance on the k-fold cross validation for different values of $k$")

    plt.xlabel("Number of nearest neighbors $k$")

    plt.xticks(k_list)

    plt.ylabel("Performance (accuracy)")

    plt.grid(True)

    plt.show()



def main(args):
    """
    The main function of the script. Do not hesitate to play with it
    and add your own code, visualization, prints, etc!

    Arguments:
        args (Namespace): arguments that were parsed from the command line (see at the end 
                          of this file). Their value can be accessed as "args.argument".
    """
    ## 1. First, we load our data and flatten the images into vectors

    ##EXTRACTED FEATURES DATASET
    if args.data_type == "features":
        feature_data = np.load('features.npz',allow_pickle=True)
        xtrain, xtest, ytrain, ytest, ctrain, ctest =feature_data['xtrain'],feature_data['xtest'],feature_data['ytrain'],feature_data['ytest'],feature_data['ctrain'],feature_data['ctest']

    ##ORIGINAL IMAGE DATASET (MS2)
    elif args.data_type == "original":
        data_dir = os.path.join(args.data_path,'dog-small-64')
        xtrain, xtest, ytrain, ytest, ctrain, ctest = load_data(data_dir)

    ##TODO: ctrain and ctest are for regression task. (To be used for Linear Regression and KNN)  
    ##TODO: xtrain, xtest, ytrain, ytest are for classification task. (To be used for Logistic Regression and KNN)

    ## 2. Then we must prepare it. This is were you can create a validation set,
    #  normalize, add bias, etc.

    # Make a validation set (it can overwrite xtest, ytest)
    if not args.test:
        ### WRITE YOUR CODE HERE
        if args.task == "breed_identifying":
            xtrain, ytrain, xtest, ytest = create_validation_set(xtrain,ytrain,0.2)
        else:
            xtrain,ctrain,xtest,ctest = create_validation_set(xtrain,ctrain,0.2)
    
    ### WRITE YOUR CODE HERE to do any other data processing

    ## For xtrain, xtest
    mean_val_x = compute_mean(xtrain)
    std_val_x = compute_std(xtrain)

    xtrain = normalize_fn(xtrain,mean_val_x,std_val_x)
    xtrain = append_bias_term(xtrain)
    xtest = normalize_fn(xtest,mean_val_x,std_val_x)
    xtest = append_bias_term(xtest)
   

    ## 3. Initialize the method you want to use.

    # Use NN (FOR MS2!)
    if args.method == "nn":
        raise NotImplementedError("This will be useful for MS2.")

    # Follow the "DummyClassifier" example for your methods
    if args.method == "dummy_classifier":
        method_obj = DummyClassifier(arg1=1, arg2=2)

    if args.method == "knn":
        method_obj = KNN(args.K,task_kind= "classification" if args.task =="breed_identifying" else "regression")

    if args.method == "linear_regression":
        method_obj = LinearRegression(args.lmda)
    
    if args.method == "logistic_regression":
        method_obj = LogisticRegression(args.lr,args.max_iters)
    
    
    ## 4. Train and evaluate the method
    if args.k_fold is not None:
        k_list = range(1,100)  
        model_performance=[]
        ## Start of the code 
        model_performance = run_cv_for_hyperparam(xtrain, ytrain, args.k_fold, k_list)
        plot_k_vs_accuracy_cv(k_list,model_performance)
        # method_obj = KNN(k=args.K,task="classification")
    
    if args.task == "center_locating":
        # Fit parameters on training data
        preds_train = method_obj.fit(xtrain, ctrain)

        # Perform inference for training and test data
        train_pred = method_obj.predict(xtrain)
        preds = method_obj.predict(xtest)

        ## Report results: performance on train and valid/test sets
        train_loss = mse_fn(train_pred, ctrain)
        loss = mse_fn(preds, ctest)
        print(f"\nTrain loss = {train_loss:.3f}% - Test loss = {loss:.3f}")

    elif args.task == "breed_identifying":

        # Fit (:=train) the method on the training data for classification task
        preds_train = method_obj.fit(xtrain, ytrain)

        # Predict on unseen data
        preds = method_obj.predict(xtest)

        ## Report results: performance on train and valid/test sets
        acc = accuracy_fn(preds_train, ytrain)
        macrof1 = macrof1_fn(preds_train, ytrain)
        print(f"\nTrain set: accuracy = {acc:.3f}% - F1-score = {macrof1:.6f}")

        acc = accuracy_fn(preds, ytest)
        macrof1 = macrof1_fn(preds, ytest)
        print(f"Test set:  accuracy = {acc:.3f}% - F1-score = {macrof1:.6f}")
    else:
        raise Exception("Invalid choice of task! Only support center_locating and breed_identifying!")

    ### WRITE YOUR CODE HERE if you want to add other outputs, visualization, etc.


if __name__ == '__main__':
    # Definition of the arguments that can be given through the command line (terminal).
    # If an argument is not given, it will take its default value as defined below.
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', default="center_locating", type=str, help="center_locating / breed_identifying")
    parser.add_argument('--method', default="dummy_classifier", type=str, help="dummy_classifier / knn / linear_regression/ logistic_regression / nn (MS2)")
    parser.add_argument('--data_path', default="data", type=str, help="path to your dataset")
    parser.add_argument('--data_type', default="features", type=str, help="features/original(MS2)")
    parser.add_argument('--lmda', type=float, default=10, help="lambda of linear/ridge regression")
    parser.add_argument('--K', type=int, default=1, help="number of neighboring datapoints used for knn")
    parser.add_argument('--lr', type=float, default=1e-5, help="learning rate for methods with learning rate")
    parser.add_argument('--max_iters', type=int, default=100, help="max iters for methods which are iterative")
    parser.add_argument('--test', action="store_true", help="train on whole training data and evaluate on the test data, otherwise use a validation set")

    ## Arguments added by me
    parser.add_argument('--k_fold',type=int,help="the number of folds for k-fold cross-validation")
    # Feel free to add more arguments here if you need!

    # MS2 arguments
    parser.add_argument('--nn_type', default="cnn", help="which network to use, can be 'Transformer' or 'cnn'")
    parser.add_argument('--nn_batch_size', type=int, default=64, help="batch size for NN training")

    # "args" will keep in memory the arguments and their values,
    # which can be accessed as "args.data", for example.
    args = parser.parse_args()
    main(args)
