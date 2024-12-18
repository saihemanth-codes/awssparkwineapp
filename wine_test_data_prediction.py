##
 # Programming assignment 
 # Course : cs-643
 # vk676
##
"""
Spark application to run tuned model with testfile
"""
import os
import sys

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import PipelineModel
from pyspark.ml.feature import StringIndexer
from pyspark.sql.functions import col

def data_cleaning(df):
    # cleaning header 
    return df.select(*(col(c).cast("double").alias(c.strip("\"")) for c in df.columns))

    

"""main function for application"""
if __name__ == "__main__":
    
    # Create spark application
    spark = SparkSession.builder \
        .appName('wine_prediction_cs643') \
        .getOrCreate()

    # create spark context to report logging information related spark
    sc = spark.sparkContext
    sc.setLogLevel('ERROR')

    # Load and parse the data file into an RDD of LabeledPoint.
    if len(sys.argv) > 3:
        print("Usage: wine_test_data_prediction.py <input_data_file> <model_path>", file=sys.stderr)
        sys.exit(-1)
    elif len(sys.argv) > 1:
        input_path = sys.argv[1]
        
        if not("/" in input_path):
            input_path = "data/csv/" + input_path
        model_path="/code/data/model/testdata.model"
        print("----Input file for test data is---")
        print(input_path)
    else:
        current_dir = os.getcwd() 
        print("-----------------------")
        print(current_dir)
        input_path = os.path.join(current_dir, "data/csv/testdata.csv")
        model_path= os.path.join(current_dir, "data/model/testdata.model")

    # read csv file in DataFram 
    df = (spark.read
          .format("csv")
          .option('header', 'true')
          .option("sep", ";")
          .option("inferschema",'true')
          .load(input_path))
    
    df1 = data_cleaning(df)
    # Split the data into training and test sets (30% held out for testing)
    # removing column not adding much value to prediction
    # removed 'residual sugar','free sulfur dioxide',  'pH',
    required_features = ['fixed acidity',
                        'volatile acidity',
                        'citric acid',
                        'chlorides',
                        'total sulfur dioxide',
                        'density',
                        'sulphates',
                        'alcohol',
                    ]
    
    # creating vector column name feature using only required_features list columns
    #assembler = VectorAssembler(inputCols=required_features, outputCol='features_1')
    #transformed_data = assembler.transform(df1)
    
    # creating classification with given input values 
    #indexer = StringIndexer(inputCol="quality", outputCol="label_1")
    #df3 = indexer.fit(transformed_data).transform(transformed_data)

   
    rf = PipelineModel.load(model_path)
    
    predictions = rf.transform(df1)
    print(predictions.show(5))
    results = predictions.select(['prediction', 'label'])
    evaluator = MulticlassClassificationEvaluator(
                                            labelCol='label', 
                                            predictionCol='prediction', 
                                            metricName='accuracy')

    # printing accuracy of above model
    accuracy = evaluator.evaluate(predictions)
    print('Test Accuracy = ', accuracy)
    metrics = MulticlassMetrics(results.rdd.map(tuple))
    print('Weighted f1 score = ', metrics.weightedFMeasure())
    sys.exit(0)
