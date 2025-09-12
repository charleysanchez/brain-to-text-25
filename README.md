# Brain To Text 2025

This repository acts as my basecamp for competing in Kaggle's brain-to-text-25 competition: [competition-link](https://github.com/charleysanchez/brain-to-text-25)

I will be competing as the solo author of this code.

---

## Attribution and License

Portions of this documentation (including the *Data Overview* section) are adapted from the **Neuroprosthetics-Lab / nejm-brain-to-text** repository.  
Original code is released under the MIT License. :contentReference[oaicite:1]{index=1}

---

### Initialization

Run the following from the root directory:

```bash
./setup.sh
```

To create a conda environment with all the required dependencies for this code to execute correctly. If working properly, the conda environment should be activateable using the command `conda activate b2txt25`.


### Data (Adapted)

> From *Neuroprosthetics-Lab / nejm-brain-to-text* (MIT License), with minor formatting changes.

The data used in this repository (which can be downloaded from Dryad, either manually or using `download_data.py`) consists of various datasets for recreating figures and training/evaluating the brain-to-text model:

- `t15_copyTask.pkl`: This file contains the online Copy Task results required for generating Figure 2.  
- `t15_personalUse.pkl`: This file contains the Conversation Mode data required for generating Figure 4.  
- `t15_copyTask_neuralData.zip`: This dataset contains the neural data for the Copy Task.  
  - There are 10,948 sentences from 45 sessions spanning 20 months. Each trial of data includes:  
    - The session date, block number, and trial number  
    - 512 neural features (2 features [-4.5 RMS threshold crossings and spike band power] per electrode, 256 electrodes), binned at 20 ms resolution. The data were recorded from the speech motor cortex via four high-density microelectrode arrays (64 electrodes each). The 512 features are ordered as follows in all data files:  
      0-64: ventral 6v threshold crossings  
      65-128: area 4 threshold crossings  
      129-192: 55b threshold crossings  
      193-256: dorsal 6v threshold crossings  
      257-320: ventral 6v spike band power  
      321-384: area 4 spike band power  
      385-448: 55b spike band power  
      449-512: dorsal 6v spike band power  
    - The ground truth sentence label  
    - The ground truth phoneme sequence label  
  - The data is split into training, validation, and test sets. The test set does not include ground truth sentence or phoneme labels.  
  - Data for each session/split is stored in `.hdf5` files. An example of how to load this data using the Python `h5py` library is provided in the `model_training/evaluate_model_helpers.py` file in the `load_h5py_file()` function.  
  - Each block of data contains sentences drawn from a range of corpuses (Switchboard, OpenWebText2, a 50-word corpus, a custom frequent-word corpus, and a corpus of random word sequences). Furthermore, the majority of the data is during attempted vocalized speaking, but some of it is during attempted silent speaking.  
- `t15_pretrained_rnn_baseline.zip`: This dataset contains the pretrained RNN baseline model checkpoint and args. An example of how to load this model and use it for inference is provided in the `model_training/evaluate_model.py` file.  

---

### Credits

- *Neuroprosthetics-Lab / nejm-brain-to-text* — original authors of the data, model baseline, and documentation.  
- This project reuses/adapts parts of their documentation under the terms of the MIT License.  

---

### License

This project (including adapted documentation) is released under the terms of the MIT License. See [LICENSE](LICENSE) (or appropriate file) for full terms.
