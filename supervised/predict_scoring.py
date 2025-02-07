
# %%
import os
# os.environ['CUDA_VISIBLE_DEVICES'] = "0"
import pandas as pd
import torch
from ConBAP import downstream_affinity,ConBAP, downstream_docking
from dataset_ConBAP import GraphDataset, PLIDataLoader
import numpy as np
from utils import *
from sklearn.metrics import mean_squared_error

# %%
def val(model, dataloader, device):
    model.eval()

    pred_list = []
    label_list = []
    for data in dataloader:
        
        with torch.no_grad():
            data['ligand_features'] = data['ligand_features'].to(device)
            data['complex_features'] = data['complex_features'].to(device)
            pred = model(data)
            label = data["ligand_features"].y
            pred_list.append(pred.detach().cpu().numpy())
            label_list.append(label.detach().cpu().numpy())
            
    pred = np.concatenate(pred_list, axis=0)
    label = np.concatenate(label_list, axis=0)

    coff = np.corrcoef(pred, label)[0, 1]
    rmse = np.sqrt(mean_squared_error(label, pred))

    model.train()

    return rmse, coff
    
# %%
data_root = './data/pdbbind/v2020-other-PL'
graph_type = 'ConBAP'
batch_size = 1

valid_dir = os.path.join(data_root, 'valid')

# test2016_dir = os.path.join(data_root, 'test2016')

data_dir = os.path.join('./data/pdbbind/v2020-other-PL')
valid_df = pd.read_csv(os.path.join('./data/pdbbind/val_new.csv'))

data_dir_redocked = os.path.join('./data/CASF-2016/data_scoring')

test2016_df = pd.read_csv(os.path.join('./data/pdbbind/data_test.csv'))

valid_set = GraphDataset(data_dir, valid_df, graph_type='ConBAP', dis_threshold=8, create=False)
valid_loader = PLIDataLoader(valid_set, batch_size=batch_size, shuffle=False, num_workers=8)

test2016_set = GraphDataset(data_dir_redocked, test2016_df, graph_type='ConBAP', dis_threshold=8, create=False)
test2016_loader = PLIDataLoader(test2016_set, batch_size=batch_size, shuffle=False, num_workers=8)



device = torch.device('cuda:0')

model = ConBAP(35, 256).to(device)
model = downstream_affinity(model, 256).to(device)
# load_model_dict(model, "./model/20230925_205502_ConBAP_repeat0/model/epoch-601, train_loss-0.0776, train_rmse-0.2787, valid_rmse-1.1926, valid_pr-0.7534.pt")
# load_model_dict(model, "./model/20231009_182510_ConBAP_repeat2/model/epoch-538, train_loss-0.0763, train_rmse-0.2761, valid_rmse-1.1418, valid_pr-0.7890.pt")
load_model_dict(model, f"./model/20231007_111336_ConBAP_repeat0/model/epoch-292, train_loss-0.1220, train_rmse-0.3493, valid_rmse-1.1663, valid_pr-0.7788.pt")
model = model.cuda()

valid_rmse, valid_coff = val(model, valid_loader, device)

test2016_rmse, test2016_coff = val(model, test2016_loader, device)


msg = "valid_rmse-%.4f, valid_r-%.4f, test2016_rmse-%.4f, test2016_r-%.4f" \
    % (valid_rmse, valid_coff, test2016_rmse, test2016_coff)
    # with open(f'./model/{checkpoint}/result.txt', 'a') as f:    # olso write the epoch
        
    #     f.write("{}:{}\n".format(epoch, msg))

        
print(msg)
# %%
