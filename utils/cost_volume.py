import torch
import numpy as np


def CostVolume(input_feature, candidate_feature, position="left", method="subtract", k=4, batch_size=4, channel=32, D=192, H=256, W=512):
    """
    Some parameters:
        position
            means whether the input feature img is left or right
        k
            the conv counts of the first stage, the feature extraction stage
    """
    origin = input_feature  # img shape : [batch_size, H // 2**k, W // 2**k, channel]
    candidate = candidate_feature
    """ if the input image is the left image, and needs to compare with the right candidate.
        Then it should move to right and pad in left"""
    if position == "left":
        leftMinusRightMove_List = []
        for disparity in range(D // 2**k):
            if disparity == 0:
                if method == "subtract":
                    """ origin method"""
                    leftMinusRightMove = origin - candidate
                else:
                    """ proposed concat mathod """
                    leftMinusRightMove = torch.cat((origin, candidate), 1)
                leftMinusRightMove_List.append(leftMinusRightMove)
            else:
                zero_padding = np.zeros((origin.shape[0], channel, disparity, origin.shape[3]))
                zero_padding = torch.from_numpy(zero_padding).float()
                zero_padding = zero_padding.cuda()

                right_move = torch.cat((zero_padding, origin), 2)

                if method == "subtract":
                    """ origin method"""
                    leftMinusRightMove = right_move[:, :, :origin.shape[2], :] - candidate
                else:
                    """ concat mathod """
                    leftMinusRightMove = torch.cat((right_move[:, :, :origin.shape[2], :], candidate), 1)

                leftMinusRightMove_List.append(leftMinusRightMove)
        cost_volume = torch.stack(leftMinusRightMove_List, dim=1)

        return cost_volume

    elif position == "right":
        rightMinusLeftMove_List = []
        for disparity in range(D // 2**k):
            if disparity == 0:
                rightMinusLeftMove = origin - candidate
                rightMinusLeftMove_List.append(rightMinusLeftMove)
            else:
                zero_padding = np.zeros((batch_size, channel, disparity, origin.shape[3]))
                zero_padding = torch.from_numpy(zero_padding).float()
                zero_padding = zero_padding.cuda()

                left_move = torch.cat((zero_padding, origin), 2)
                rightMinusLeftMove = left_move[:, :, :origin.shape[2], :] - candidate
                rightMinusLeftMove_List.append(rightMinusLeftMove)
        cost_volume = torch.stack(rightMinusLeftMove_List, dim=1)

        return cost_volume