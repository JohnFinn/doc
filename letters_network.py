from numpy import array
from PIL import Image
from torch import nn, optim, no_grad, exp
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from pandas import read_csv
from string import ascii_lowercase, ascii_uppercase
from time import time


def letters_dataset() -> dict:
    letters = dict()
    cyr_u = 'БГДЁЖЗИЙЛПФЦЧШЩЪЫЬЭЮЯ'
    cyr_l = cyr_u.lower() + 'мнт'
    for counter, item in enumerate(ascii_lowercase + ascii_uppercase + cyr_l + cyr_u):
        letters[item] = counter
    return letters


class LettersDataset(Dataset):

    letters = letters_dataset()

    def __init__(self, df, transform=None):
        self.df = df
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        if self.transform:
            return self.transform(array(Image.open(self.df.iloc[index, 0]))), \
                self.letters[self.df.iloc[index, 1]]
        return transforms.ToTensor()(array(Image.open(self.df.iloc[index, 0]))), \
            self.letters[self.df.iloc[index, 1]]


class DatasetTestTrain:

    def __init__(self, dataset):
        transform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize((0.5,), (0.5,)),
                                        ])
        self.__len = len(dataset)
        test = LettersDataset(dataset.iloc[:int(self.__len / 3)].reset_index(drop=True), transform=transform)
        train = LettersDataset(dataset.iloc[int(self.__len / 3):].reset_index(drop=True), transform=transform)
        self.test_loader = DataLoader(test, batch_size=1)
        self.train_loader = DataLoader(train, batch_size=128)

    def __len__(self):
        return self.__len


def network(dataset_csv_path: str):
    csv_data = read_csv(dataset_csv_path)[1:].sample(frac=1)
    dataset = DatasetTestTrain(csv_data)
    net = nn.Sequential(nn.Linear(32 * 32, 512),
                        nn.ReLU(),
                        nn.Linear(512, 256),
                        nn.ReLU(),
                        nn.Linear(256, len(LettersDataset.letters)),
                        nn.LogSoftmax(dim=1))
    print(net)

    criterion = nn.NLLLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.003, momentum=0.9)
    time_start = time()
    epochs = 20

    for e in range(epochs):
        current_loss = 0
        for images, labels in dataset.train_loader:
            images = images.view(-1, 32 * 32)
            optimizer.zero_grad()
            output = net(images)
            loss = criterion(output, labels)
            loss.backward()
            optimizer.step()
            current_loss += loss.item()

        print("epoch {} ---- loss: {}".format(e, current_loss / len(dataset.train_loader)))
        print("training time: ", (time() - time_start) / 60)

    correct_count = 0
    for images, labels in dataset.test_loader:
        for i in range(len(labels)):
            image = images.view(-1, 32 * 32)
            with no_grad():
                log_ps = net(image)
            ps = exp(log_ps)
            tmp = list(ps.numpy()[0])
            prediction_label = tmp.index(max(tmp))
            real_label = labels.numpy()[i]
            if real_label == prediction_label:
                correct_count += 1

    print("all images: ", len(dataset))
    print("accuracy: ", correct_count / len(dataset.test_loader))
