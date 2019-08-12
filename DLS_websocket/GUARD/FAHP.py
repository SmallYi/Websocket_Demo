import numpy as np
import pandas as pd
import csv

class FAHP_Method():
    def __init__(self):
        pass

    def get_global_weight(self,total_matrix):
        m = total_matrix[0].shape[0]
        n = len(total_matrix)
        weight = []
        for i in range(0,n):
            if self.judge_consistency(total_matrix[i]):
                w = self.get_weight(total_matrix[i])
            else:
                total_matrix[i] = self.turn_consistency(total_matrix[i])
                w = self.get_weight(total_matrix[i])
            if i == 0:
                w0 = w
            else:
                for j in range(0,len(w)):
                    w[j] = round((w[j] * w0[i-1]),4)
                weight += w
        return weight




    def get_weight(self,judge_matrix):
        n = len(judge_matrix)
        a = []
        weigh = []
        if self.judge_consistency(judge_matrix):
            pass
        else:
            judge_matrix = self.turn_consistency(judge_matrix)
        for i in range(0,n):
            temp = 0
            for j in range(0,n):
                temp += judge_matrix[i,j]
            w = round((temp + n / 2 - 1) / (n * (n - 1)), 2)
            weigh.append(w)
        weigh = self.Vector_normal(weigh)
        return weigh


    def judge_consistency(self,matrix):
        n = len(matrix)
        for i in range(0,n):
            for j in range(0,n):
                for k in range(0,n):
                    if matrix[i,j] == round((matrix[i,k] - matrix[j,k] + 0.5),1):
                        pass
                    else:
                        return 0
        return 1

    def turn_consistency(self,martix):
        r = []
        n = len(martix)
        for i in range(0,n):
            temp = 0
            for k in range(0,n):
                temp += martix[i,k]
            r.append(temp)
        for i in range(0,n):
            for j in range(0,n):
                martix[i,j] = round((((r[i] - r[j])/(2*(n-1))) + 0.5),2)
        return martix


    def Vector_normal(self,vec):
        n = len(vec)
        s = sum(vec)
        for i in range(0,n):
            vec[i] /= s
        return vec


class Evaluation():
    def __init__(self):
        pass

    def Membership_function(self,judge_set,indicator):
        n = len(judge_set)
        if judge_set[0] > judge_set[1]:
            tend = 0
        else:
            tend = 1
        menbership_vector = []
        for i in range(0,n):
            member = 0
            if i-1 >= 0 and indicator >= judge_set[i-1] and indicator < judge_set[i]:
                member = round((indicator - judge_set[i-1]) / (judge_set[i] - judge_set[i-1]), 2)
            elif i+1 <= n-1 and indicator >= judge_set[i] and indicator < judge_set[i+1]:
                member = round((judge_set[i+1] - indicator) / (judge_set[i+1] - judge_set[i]), 2)
            elif tend == 1:
                if indicator < judge_set[0] and i == 0:
                    member = 1
                elif indicator > judge_set[-1] and i == n-1:
                    member = 1
                else:
                    member = 0
            elif tend == 0:
                if indicator < judge_set[-1] and i == n-1:
                    member = 1
                elif indicator > judge_set[0] and i == 0:
                    member = 1
                else:
                    member = 0
            menbership_vector.append(member)
        return menbership_vector


    def Membership_matrix(self,matrix_level,vector_indicator):
        matrix_len = len(matrix_level)
        matrix_degree = []
        for i in range(0,matrix_len):
            level = matrix_level[i]
            indicator = vector_indicator[i]
            degree = self.Membership_function(level,indicator)
            matrix_degree.append(degree)
        return matrix_degree


    def fuzzy_evaluate_result(self,weight_vector,matrix_degree):
        result = []
        len_index = len(weight_vector)
        for i in range(4):
            v = 0
            for j in range(len_index):
                v += weight_vector[j] * matrix_degree[j][i]
            result.append(round(v,2))
        s = sum(result)
        for i in range(4):
            result[i] = round((result[i] / s),2)
        return result

