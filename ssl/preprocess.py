"""
Preprocess the data for training/validating/testing
Be advised to run the remove_duplicates.py on raw json files (remove overlapping docs between train and valid/test)
 before running this preprocess
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os

import torch

import config
import pykp.io

parser = argparse.ArgumentParser(
    description='preprocess.py',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# **Preprocess Options**
parser.add_argument('-dataset_name', required=True,
                    help="Name of dataset")
parser.add_argument('-source_dataset_dir', required=True,
                    help="The path to the source data (raw json).")
parser.add_argument('-output_path_prefix', default='data',
                    help="Output file for the prepared data")

config.preprocess_opts(parser)
opt = parser.parse_args()

# input path of each json file
opt.source_train_file = os.path.join(opt.source_dataset_dir, '%s_training.json' % (opt.dataset_name))
opt.source_valid_file = os.path.join(opt.source_dataset_dir, '%s_validation.json' % (opt.dataset_name))
opt.source_test_file = os.path.join(opt.source_dataset_dir, '%s_testing.json' % (opt.dataset_name))

# output path for exporting the processed dataset
opt.output_path = os.path.join(opt.output_path_prefix, opt.dataset_name)
# output path for exporting the processed dataset
opt.subset_output_path = os.path.join(opt.output_path_prefix, opt.dataset_name+'_small')

if not os.path.exists(opt.output_path):
    os.makedirs(opt.output_path)
if not os.path.exists(opt.subset_output_path):
    os.makedirs(opt.subset_output_path)

def main():
    if opt.dataset_name == 'kp20k':
        src_fields = ['title', 'abstract']
        trg_fields = ['keyword']
        valid_check=True
    elif opt.dataset_name == 'stackexchange':
        src_fields = ['title', 'question']
        trg_fields = ['tags']
        valid_check=True
    elif opt.dataset_name == 'twacg':
        src_fields = ['observation']
        trg_fields = ['admissible_commands']
        valid_check=False
    else:
        raise Exception('Unsupported dataset name=%s' % opt.dataset_name)

    print("Loading training/validation/test data...")
    tokenized_train_pairs = pykp.io.load_src_trgs_pairs(source_json_path=opt.source_train_file,
                                                        dataset_name=opt.dataset_name,
                                                        src_fields=src_fields,
                                                        trg_fields=trg_fields,
                                                        opt=opt,
                                                        valid_check=valid_check)

    tokenized_valid_pairs = pykp.io.load_src_trgs_pairs(source_json_path=opt.source_valid_file,
                                                        dataset_name=opt.dataset_name,
                                                        src_fields=src_fields,
                                                        trg_fields=trg_fields,
                                                        opt=opt,
                                                        valid_check=valid_check)

    tokenized_test_pairs = pykp.io.load_src_trgs_pairs(source_json_path=opt.source_test_file,
                                                       dataset_name=opt.dataset_name,
                                                       src_fields=src_fields,
                                                       trg_fields=trg_fields,
                                                       opt=opt,
                                                       valid_check=valid_check)

    print("Building Vocab...")
    word2id, id2word, vocab = pykp.io.build_vocab(tokenized_train_pairs, opt)
    print('Vocab size = %d' % len(vocab))
    if opt.vocab_size > len(vocab):
        opt.vocab_size = len(vocab)
        print('Reset vocab size to %d' % opt.vocab_size)

    print("Dumping dict to disk")
    opt.vocab_path = os.path.join(opt.subset_output_path, opt.dataset_name + '.vocab.pt')
    torch.save([word2id, id2word, vocab], open(opt.vocab_path, 'wb'))
    opt.vocab_path = os.path.join(opt.output_path, opt.dataset_name + '.vocab.pt')
    torch.save([word2id, id2word, vocab], open(opt.vocab_path, 'wb'))

    print("Exporting a small dataset to %s (for debugging), "
          "size of train/valid/test is 20000" % opt.subset_output_path)
    pykp.io.process_and_export_dataset(tokenized_train_pairs[:20000],
                                       word2id, id2word,
                                       opt,
                                       opt.subset_output_path,
                                       dataset_name=opt.dataset_name,
                                       data_type='train')

    pykp.io.process_and_export_dataset(tokenized_valid_pairs,
                                       word2id, id2word,
                                       opt,
                                       opt.subset_output_path,
                                       dataset_name=opt.dataset_name,
                                       data_type='valid',
                                       include_original=True)

    pykp.io.process_and_export_dataset(tokenized_test_pairs,
                                       word2id, id2word,
                                       opt,
                                       opt.subset_output_path,
                                       dataset_name=opt.dataset_name,
                                       data_type='test',
                                       include_original=True)

    print("Exporting complete dataset to %s" % opt.output_path)
    pykp.io.process_and_export_dataset(tokenized_train_pairs,
                                       word2id, id2word,
                                       opt,
                                       opt.output_path,
                                       dataset_name=opt.dataset_name,
                                       data_type='train')

    pykp.io.process_and_export_dataset(tokenized_valid_pairs,
                                       word2id, id2word,
                                       opt,
                                       opt.output_path,
                                       dataset_name=opt.dataset_name,
                                       data_type='valid',
                                       include_original=True)

    pykp.io.process_and_export_dataset(tokenized_test_pairs,
                                       word2id, id2word,
                                       opt,
                                       opt.output_path,
                                       dataset_name=opt.dataset_name,
                                       data_type='test',
                                       include_original=True)

if __name__ == "__main__":
    main()
