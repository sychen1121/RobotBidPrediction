import numpy as np
from datetime import datetime as dt
from time import time
from sklearn.metrics import roc_auc_score
import networkx as nx
import feature as ft

def main():
	print("main")

# evaluation
# predictFile and gtFile need the same amount of rows
def evaluate(predictFile="../data/train.csv", gtFile="../data/train.csv", outputFile='../result/score.csv'):
	preds = list()
	gts = list()
	with open(predictFile, 'r') as fi:
		fi.readline()
		for line in fi:
			# print(line.strip().split(',')[1])
			pred = float(line.strip().split(',')[-1])
			preds.append(pred)
	with open(gtFile, 'r') as fi:
		fi.readline()
		for line in fi:
			gt = int(float(line.strip().split(',')[-1]))
			gts.append(gt)
	score = roc_auc_score(gts, preds)
	print("AUC:"+str(score))
	with open(outputFile, 'a') as fo:
		# outputStr = str(time())+": "+str(score)+'\n'
		outputStr = str(dt.now())+": "+str(score)+'\n'
		fo.write(outputStr)
	return score

def createGraph(bidderFile="../data/train.csv", bidderFile2="../data/test.csv", bidFile="../data/bid_short.csv"):
	s= time()
	g = nx.Graph()
	bidders1 = initNode(g, bidderFile)
	bidders2 = initNode(g, bidderFile2)
	auctions = initEdge(g, bidFile)
	bidders = bidders1+bidders2
	print("Init Graph Over:"+str(time()-s))
	updateAuction(g, auctions)
	updateBidder(g, bidders)
	ipDistri = updateIpDistri(g)
	print(g.node["ewmzr"])
	print(g.node["8dac2b259fd1c6d1120e519fb1ac14fbqvax8"])
	print("Update Graph Over:"+str(time()-s))
	# print(g.nodes())


def initNode(g, bidderFile):
	titles = list()
	bidders = list()
	with open(bidderFile, 'r') as fi:
		titles = fi.readline().strip().split(',')
		for line in fi:
			# attrs = {"type": "bidder"}
			data = line.strip().split(',')
			bidder = data[0]
			bidders.append(bidder)
			g.add_node(bidder, type="bidder", ips=list(), device=dict(), country=dict())
			for i in range(1,len(data)):
				g.node[bidder][titles[i]] = data[i]
	return bidders

def initEdge(g, bidFile):
	auctions = list()
	with open(bidFile, 'r') as fi:
		titles = fi.readline().strip().split(',')
		for line in fi:
			data = line.strip().split(',')
			bid = data[0]
			print(bid)
			bidder=data[1]
			auction=data[2]
			merchandise = data[3]
			device = data[4]
			time = data[5]
			country = data[6]
			ip = data[7]
			url = data[8]
			bidAttrs = {"device":device, "time":time, "country":country, "ip":ip, "url":url}
			# revise bidder information
			ips = g.node[bidder]["ips"]
			countryDistri = g.node[bidder]["countryDistri"]
			deviceDistri = g.node[bidder]["deviceDistri"]
			if ip not in ips:
				ips.append(ip)
				g.node[bidder]["ips"] = ips
			countryDistri[country] = countryDistri.get(country,0)+1
			deviceDistri[device] = deviceDistri.get(device, 0)+1
			g.node[bidder]["countryDistri"] = countryDistri
			g.node[bidder]["deviceDistri"] = deviceDistri
			# add auction
			if g.has_node(auction):
				g.add_node(auction, type="auction",merchandise=merchandise, bidders=[bidder])
			else:
				g.node[auction]["bidders"] = g.node[auction]["bidders"].append(bidder)
			# bidders = 
			auctions.append(auction)
			# add and revise edge information
			if g.has_edge(auction, bidder):
				num = g.edge[auction][bidder]["num"]+1
				bids = g.edge[auction][bidder]["bids"]
				bids[bid] = bidAttrs
			else:
				num = 1
				bids = {bid:bidAttrs}
			g.add_edge(auction, bidder, num=num, bids=bids)
	return auctions

# bidderDistri: auction bid distribution of bidder, sum =1
def updateAuction(g, auctions):
	# update bidders inform
	for auction in auctions:
		edges = g.edge[auction]
		total = float()
		bidderBidRatio = dict()
		nums = list()
		bidders = list()
		attrs = g.node[auction]
		for (b, attr) in edges.items():
			num = attr["num"]
			total = total + num
			bidders.append(b)
			nums.append(num)
		for i in range(len(bidders)):
			bidderBidRatio[bidders[i]] = nums[i]/total
		attrs["bidderDistri"] = bidderBidRatio
		# g.add_node(auction, )
		g.add_node(auction, attrs)



# auctionRatio: bidder bid ratio in that auction, sum != 1
# auctionDistri: bidder bid distribution of bidding auctions, sum = 1
# avgBidNum: bidder average number of bid
def updateBidder(g, bidders):
	for bidder in bidders:
		edges = g.edge[bidder]
		auctionRatios = dict()
		auctionDistri = dict()
		total = int()
		# update ratio from auctions
		for (auction, attr) in edges.items():
			auctionRatios[auction] = g.node[auction]["bidderDistri"][bidder]
			num = attr["num"]
			total = total + num
			auctionDistri[auction] = num
		# update distribution 
		for auction in edges.keys():
			auctionDistri[auction] = auctionDistri[auction]/total
		g.node[bidder]["auctionDistri"] = auctionDistri
		g.node[bidder]["auctionRatios"] =  auctionRatios
		g.node[bidder]["avgBidNum"] = total/len(edges)


def updateIpDistri(g, bidders):
	ipDistri = dict()
	for bidder in bidders:
		ips = g.node[bidder]["ips"]
		for ip in ips:
			ipDistri[ip] = ipDistri.get(ip, list()).append(bidder)
	return ipDistri


def writeFeature():
	print("write feature")

if __name__ == "__main__":
	# main()
	createGraph()
	# evaluate()