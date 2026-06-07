# Algorithm for k-means clusering 
#1. elbow method gives number of clusters:
#2.  take k  random centroid
#3. Now calculate eucledian bistance between data point and each centroid. 
# then data point lies in a cluster such taht distance is minimal
#4. recalculate centroid using same cluster data points
#5. repeat srep 3 and 4  untill no chanhe in cluster data points or centroid


import numpy as np
import random
class KMeans:
    def __init__(self,n_cluster,max_itter):
        self.n_cluster=n_cluster
        self.max_itter=max_itter
        self.centroid=None
        
    def fit_predict(self,X):
        random_centroid=random.sample(range(0,X.shape[0]),self.n_cluster)
        self.centroid=X[random_centroid]

        for i in range(self.max_itter):
            cluster_group=self.Assign_cluster(X)
            old_centroids=self.centroid
            self.centroid=self.move_centroids(X,cluster_group)

            if(old_centroids==self.centroid).all():
                break

        return cluster_group

        

    def Assign_cluster(self,X):
        distance=[]
        cluster_group=[]

        for row in X:
            for centroid in self.centroid:
                distance.append(np.sqrt(np.dot(row-centroid,row-centroid)))

            min_distance=np.min(distance)
            index_pos=distance.index(min_distance)
            distance.clear()
            cluster_group.append(index_pos)

        return np.array(cluster_group)
    
    def move_centroids(self,X,cluster_group):
        new_centroid=[]
        cluster_type=np.unique(cluster_group)

        for type in cluster_type:
            new_centroid.append(X[cluster_group==type].mean(axis=0))
        
        return np.array(new_centroid)
