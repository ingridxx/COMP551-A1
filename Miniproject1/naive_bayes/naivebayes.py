# Naive Baye's implementation
# Feel free to edit/change/delete anything, I honestly don't know if I did this right -Ali
import numpy as np
import pandas as pd
from random import seed
from random import randrange
from math import sqrt
from math import pi
from math import exp
from sklearn.preprocessing import LabelEncoder


class NaiveBaye:

    def separate_data(self, dataset):
        separated = dict()
        for i in range(len(dataset)):
            vector = dataset[i]
            class_value = vector[-1]
            if (class_value not in separated):
                separated[class_value] = list()
            separated[class_value].append(vector)
        return separated

    # Calculate the following for each data point:
    #   - mean
    #   - standard deviation
    #   - count
    def dataset_statistics(self, dataset):
        summaries = [(np.mean(column), np.std(column), len(column)) for column in zip(*dataset)]
        del(summaries[-1])
        return summaries

    # Statistics for each row
    def class_statistics(self, dataset):
        separated = self.separate_data(dataset)
        summaries = dict()
        for class_value, rows in separated.items():
            summaries[class_value] = self.dataset_statistics(rows)
        return summaries

    def probability(self, x, mean, stdev):
        if stdev == 0:
            stdev = 0.0001
            # return 0
        exponent = exp(-((x - mean)**2 / (2 * stdev**2)))
        return (1 / (sqrt(2 * pi) * stdev)) * exponent

    def likelihood(self, summaries, row):
        total_rows = sum([summaries[label][0][2] for label in summaries])
        probabilities = dict()
        for class_value, class_summaries in summaries.items():
            probabilities[class_value] = summaries[class_value][0][2] / float(total_rows)
            for i in range(len(class_summaries)):
                mean, stdev, count = class_summaries[i]
                probabilities[class_value] *= self.probability(row[i], mean, stdev)
        return probabilities

    def predict(self, summaries, row):
        probabilities = self.likelihood(summaries, row)
        best_label, best_prob = None, -1
        for class_value, probability in probabilities.items():
            if best_label is None or probability > best_prob:
                best_prob = probability
                best_label = class_value
        return best_label

    def fit(self, train, test):
        summarize = self.class_statistics(train)
        predictions = list()
        for row in test:
            output = self.predict(summarize, row)
            predictions.append(output)
        return(predictions)

    # Calculate accuracy percentage
    def evaluate_acc(self, y, y_hat):
        correct_predictions = 0
        for i in range(len(y)):
            if y[i] == y_hat[i]:
                correct_predictions += 1
        return correct_predictions / float(len(y)) * 100.0

    # K-fold cross validation
    # --------------------------------------------------------------------------------#
    def cross_validation_split(self, dataset, k_folds):
        dataset_split = list()
        dataset_copy = list(dataset)
        fold_size = int(len(dataset) / k_folds)
        for _ in range(k_folds):
            fold = list()
            while len(fold) < fold_size:
                index = randrange(len(dataset_copy))
                fold.append(dataset_copy.pop(index))
            dataset_split.append(fold)
        return dataset_split

    # Evaluate an algorithm using a cross validation split
    def evaluate_algorithm(self, dataset, algorithm, k_folds, *args):
        folds = self.cross_validation_split(dataset, k_folds)
        scores = list()
        for fold in folds:
            train_set = list(folds)
            train_set.remove(fold)
            train_set = sum(train_set, [])
            test_set = list()
            for row in fold:
                row_copy = list(row)
                test_set.append(row_copy)
                row_copy[-1] = None
            predicted = algorithm(train_set, test_set, *args)
            actual = [row[-1] for row in fold]
            accuracy = self.evaluate_acc(actual, predicted)
            scores.append(accuracy)
        return scores
    # --------------------------------------------------------------------------------#

    def main(self):

        # Ionosphere Dataset
        dataframe = pd.read_csv("data/ionosphere.data", header=None)
        array = dataframe.values
        X = array[:, :-1]
        y = array[:, -1:]
        y = LabelEncoder().fit_transform(array[:, -1:].ravel())
        X = X.tolist()
        y = y.tolist()
        array = X
        for i in range(len(X)):
            array[i].append(y[i])
        k_folds = 5
        scores = self.evaluate_algorithm(array, self.fit, k_folds)
        print('Scores: %s' % scores)
        print('Mean Accuracy: %.3f%%' % (sum(scores) / float(len(scores))))

        # Adult Dataset
        dataframe = pd.read_csv("data/adult.data", header=None)
        dataframe = dataframe.apply(LabelEncoder().fit_transform)
        values = dataframe.values
        array = values.tolist()
        k_folds = 5
        scores = self.evaluate_algorithm(array, self.fit, k_folds)
        print('Scores: %s' % scores)
        print('Mean Accuracy: %.3f%%' % (sum(scores) / float(len(scores))))

        # Breast-Cancer Dataset
        dataframe = pd.read_csv("data/breast-cancer.data", header=None)
        dataframe = dataframe.replace(to_replace="?", value=np.nan)
        dataframe = dataframe.dropna()
        dataframe = dataframe.apply(LabelEncoder().fit_transform)
        values = dataframe.values
        array = values.tolist()
        k_folds = 5
        scores = self.evaluate_algorithm(array, self.fit, k_folds)
        print('Scores: %s' % scores)
        print('Mean Accuracy: %.3f%%' % (sum(scores) / float(len(scores))))

        # Wine Dataset
        dataframe = pd.read_csv("data/winequality-red.csv", sep=';', header=None, skiprows=1)
        values = dataframe.values
        array = values.tolist()
        k_folds = 5
        scores = self.evaluate_algorithm(array, self.fit, k_folds)
        print('Scores: %s' % scores)
        print('Mean Accuracy: %.3f%%' % (sum(scores) / float(len(scores))))


if __name__ == '__main__':
    nm = NaiveBaye()
    nm.main()
