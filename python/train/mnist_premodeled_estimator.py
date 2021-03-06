from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)

tf.app.flags.DEFINE_integer('steps', 10000, 'The number of steps to train a model')
tf.app.flags.DEFINE_string('model_dir', '/tmp/mnist_premodeled_estimator', 'Dir to save a model and checkpoints')
tf.app.flags.DEFINE_string('saved_dir', './models/', 'Dir to save a model for TF serving')
FLAGS = tf.app.flags.FLAGS

INPUT_FEATURE = 'image'


def serving_input_receiver_fn():
    inputs = {
        INPUT_FEATURE: tf.placeholder(tf.float32, [None, 28, 28, 1]),
    }
    return tf.estimator.export.ServingInputReceiver(inputs, inputs)


def main(_):
    # Load training and eval data
    mnist = tf.contrib.learn.datasets.load_dataset("mnist")
    train_data = mnist.train.images  # Returns np.array
    train_labels = np.asarray(mnist.train.labels, dtype=np.int32)
    eval_data = mnist.test.images  # Returns np.array
    eval_labels = np.asarray(mnist.test.labels, dtype=np.int32)

    # reshape images
    # To have input as an image, we reshape images beforehand.
    train_data = train_data.reshape(train_data.shape[0], 28, 28, 1)
    eval_data = eval_data.reshape(eval_data.shape[0], 28, 28, 1)

    # feature columns
    feature_columns = [tf.feature_column.numeric_column(INPUT_FEATURE, shape=[28, 28, 1])]

    # Create the Estimator
    training_config = tf.estimator.RunConfig(
        model_dir=FLAGS.model_dir,
        save_summary_steps=100,
        save_checkpoints_steps=100)
    classifier = tf.estimator.DNNClassifier(
        config=training_config,
        feature_columns=feature_columns,
        hidden_units=[256, 32],
        optimizer=tf.train.AdamOptimizer(1e-4),
        n_classes=10,
        dropout=0.1,
        model_dir=FLAGS.model_dir
    )

    # Train the model
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={INPUT_FEATURE: train_data},
        y=train_labels,
        batch_size=100,
        num_epochs=None,
        shuffle=True)
    classifier.train(input_fn=train_input_fn, steps=FLAGS.steps)

    # Evaluate the model and print results
    eval_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={INPUT_FEATURE: eval_data},
        y=eval_labels,
        num_epochs=1,
        shuffle=False)
    eval_results = classifier.evaluate(input_fn=eval_input_fn)
    print(eval_results)

    # Save the model
    classifier.export_savedmodel(FLAGS.saved_dir,
                                 serving_input_receiver_fn=serving_input_receiver_fn)


if __name__ == "__main__":
    tf.app.run()
