# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
import argparse
from pathlib import Path
import numpy as np
import tensorflow as tf
from common import LABELS, SIZE, image_array, read_rows, save_json

def dataset(rows, batch, training=False):
    def gen():
        for row in rows:
            yield image_array(row['path']), np.int32(LABELS.index(row['label']))
    ds = tf.data.Dataset.from_generator(gen, output_signature=(
        tf.TensorSpec((SIZE, SIZE, 3), tf.float32), tf.TensorSpec((), tf.int32)))
    if training:
        ds = ds.shuffle(len(rows), seed=42, reshuffle_each_iteration=True)
    return ds.batch(batch).prefetch(tf.data.AUTOTUNE)

def main(a):
    tf.keras.utils.set_random_seed(a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    train_rows, val_rows = read_rows(Path(a.data)/'train.csv'), read_rows(Path(a.data)/'val.csv')
    train_ds, val_ds = dataset(train_rows, a.batch, True), dataset(val_rows, a.batch)
    base = tf.keras.applications.MobileNetV2(input_shape=(SIZE, SIZE, 3),
        alpha=a.alpha, include_top=False, weights=None if a.weights == 'none' else 'imagenet')
    base.trainable = False
    inputs = tf.keras.Input((SIZE, SIZE, 3), name='rgb_0_255')
    aug = tf.keras.Sequential([tf.keras.layers.RandomFlip('horizontal'),
        tf.keras.layers.RandomRotation(.04), tf.keras.layers.RandomZoom(.08)], name='augmentation')
    # Keep an augmentation-free inference graph for a stable TFLite export.
    normalizer = tf.keras.layers.Rescaling(1/127.5, offset=-1, name='normalize')
    pooling = tf.keras.layers.GlobalAveragePooling2D()
    dropout = tf.keras.layers.Dropout(.25)
    head = tf.keras.layers.Dense(3, activation='softmax', name='probabilities')
    def forward(x):
        return head(dropout(pooling(base(normalizer(x), training=False))))
    model = tf.keras.Model(inputs, forward(aug(inputs)))
    counts = np.bincount([LABELS.index(r['label']) for r in train_rows], minlength=3)
    if np.any(counts == 0):
        raise ValueError('Missing training label')
    weights = {i: len(train_rows)/(3*int(n)) for i,n in enumerate(counts)}
    def callbacks(stage):
        return [tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True),
                tf.keras.callbacks.CSVLogger(str(out/f'{stage}.csv'))]
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                  loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.fit(train_ds, validation_data=val_ds, epochs=a.epochs,
              class_weight=weights, callbacks=callbacks('head'))
    first_loss = float(model.evaluate(val_ds, verbose=0)[0])
    model.save_weights(out/'head.weights.h5')
    if a.fine_epochs:
        base.trainable = True
        for layer in base.layers[:-30]:
            layer.trainable = False
        for layer in base.layers:
            if isinstance(layer, tf.keras.layers.BatchNormalization):
                layer.trainable = False
        model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
                      loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(train_ds, validation_data=val_ds, epochs=a.fine_epochs,
                  class_weight=weights, callbacks=callbacks('fine'))
        if float(model.evaluate(val_ds, verbose=0)[0]) > first_loss:
            model.load_weights(out/'head.weights.h5')
    infer_inputs = tf.keras.Input((SIZE, SIZE, 3), name='rgb_0_255')
    inference = tf.keras.Model(infer_inputs, forward(infer_inputs))
    inference.save(out/'model.keras')
    save_json(out/'training_config.json', {**vars(a), 'labels': LABELS,
        'food_types': sorted(set(r['food_type'] for r in train_rows)),
        'tensorflow': tf.__version__, 'status': 'research_unvalidated'})

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data', default='data/processed')
    p.add_argument('--out', default='artifacts')
    p.add_argument('--epochs', type=int, default=15)
    p.add_argument('--fine-epochs', type=int, default=10)
    p.add_argument('--batch', type=int, default=16)
    p.add_argument('--alpha', type=float, default=.75)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--weights', choices=['imagenet', 'none'], default='imagenet')
    main(p.parse_args())
