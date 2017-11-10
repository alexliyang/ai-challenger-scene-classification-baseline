__all__ = ['DataLoader']

import numpy as np

import sampler as _sampler
from mxnet import nd


def _batchify(batch):
    """Collate data into batch."""
    im_name, im1, im2, im3, im4 = zip(*batch)
    im1 = nd.stack(*im1)
    im2 = nd.stack(*im2)
    im3 = nd.stack(*im3)
    im4 = nd.stack(*im4)
    return im_name, im1, im2, im3, im4


class DataLoader(object):
    """Loads data from a dataset and returns mini-batches of data.
    Parameters
    ----------
    dataset : Dataset
        Source dataset. Note that numpy and mxnet arrays can be directly used
        as a Dataset.
    batch_size : int
        Size of mini-batch.
    shuffle : bool
        Whether to shuffle the samples.
    sampler : Sampler
        The sampler to use. Either specify sampler or shuffle, not both.
    last_batch : {'keep', 'discard', 'rollover'}
        How to handle the last batch if batch_size does not evenly divide
        `len(dataset)`.
        keep - A batch with less samples than previous batches is returned.
        discard - The last batch is discarded if its incomplete.
        rollover - The remaining samples are rolled over to the next epoch.
    batch_sampler : Sampler
        A sampler that returns mini-batches. Do not specify batch_size,
        shuffle, sampler, and last_batch if batch_sampler is specified.
    """

    def __init__(self,
                 dataset,
                 batch_size=None,
                 shuffle=False,
                 sampler=None,
                 last_batch=None,
                 collate_fn=_batchify,
                 batch_sampler=None):
        self._dataset = dataset
        self.collate_fn = collate_fn
        if batch_sampler is None:
            if batch_size is None:
                raise ValueError("batch_size must be specified unless " \
                                 "batch_sampler is specified")
            if sampler is None:
                if shuffle:
                    sampler = _sampler.RandomSampler(len(dataset))
                else:
                    sampler = _sampler.SequentialSampler(len(dataset))
            elif shuffle:
                raise ValueError(
                    "shuffle must not be specified if sampler is specified")

            batch_sampler = _sampler.BatchSampler(sampler, batch_size,
                                                  last_batch
                                                  if last_batch else 'keep')
        elif batch_size is not None or shuffle or sampler is not None or \
                last_batch is not None:
            raise ValueError("batch_size, shuffle, sampler and last_batch must " \
                             "not be specified if batch_sampler is specified.")

        self._batch_sampler = batch_sampler

    def __iter__(self):
        for batch in self._batch_sampler:
            yield self.collate_fn([self._dataset[idx] for idx in batch])

    def __len__(self):
        return len(self._batch_sampler)