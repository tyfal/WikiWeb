# -*- coding: utf-8 -*-

"""Main module.
Created on Fri Nov 11 00:45:52 2016
@author: tfalcoff
"""
from bs4 import BeautifulSoup
import networkx as nx
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *
import numpy as np
import requests, string, time



class WikiWeb:
    
    
    def __init__(self, url):
        
        self.url = url
        self.page = requests.get(self.url).text
        self.soup = BeautifulSoup(self.page, 'lxml')
                
    
    def links(self):
        
        #page title
        n_title = ''
        for char in self.soup.title:
            if char in string.punctuation:
                char = ' '
            n_title += char
        l_title = n_title.split(' ')
        l_title = l_title[:-2]            
        title = '_'.join(l_title)
        
        #wiki links    
        links=[]
        [links.append(link['href']) for link in self.soup.find_all('a', href=True)]
        commons=['/wiki/International_Standard_Book_Number', '/wiki/Digital_object_identifier']
        n_links=[]
        for link in links:
            if link[:6] == '/wiki/' and ':' not in link and link not in commons:
                if 'Main_Page' not in link and link[6:] != title:
                    if '#' not in link:
                        if link not in n_links:
                            n_links.append(link)
        links = n_links
        
        return links
        
        
    def text(self):
        
        #page text (dirty)
        texts = self.soup.find_all(text=True)
        '''
        n_texts = []
        for line in texts:
            n_line = line.split(' ')
            [n_texts.append(word) for word in n_line]
        text = n_texts
        '''
        text=[]
        for line in texts:
            if line.count(' ') > 1:
                text.append(line)
        
        return text
        
        #get hrefs too and index sentence after href
        
        
    def matrix(self):
        
        dict_links = {}
        matrix = []

        #dictionary from self.list outputs
        links = WikiWeb(self.url).links()
        wiki = 'https://en.wikipedia.org'
        for link in links:
            if link not in dict_links:
                dict_links[link] = (WikiWeb(wiki+link).links())
                
        #matrix mapping connections
        for a_link in links:
            array = []
            for b_link in links:
                if b_link in dict_links[a_link]:
                    array.append(1)
                else: 
                    array.append(0)
                    
            matrix.append(array)
        
        return matrix
        
        
    def network(self):

        #from https://plot.ly/ipython-notebooks/networks/

        def scatter_edges(G, pos, line_color='#888', line_width=.5):
            trace = Scatter(x=[], y=[], mode='lines')
            for edge in G.edges():
                trace['x'] += [pos[edge[0]][0],pos[edge[1]][0], None]
                trace['y'] += [pos[edge[0]][1],pos[edge[1]][1], None]  
                trace['hoverinfo']='none'
                trace['line']['width']=line_width
                if line_color is not None: # when it is None a default Plotly color is used
                    trace['line']['color']=line_color
            return trace            
        
            
        def scatter_nodes(pos, labels=None, size=20):
            # pos is the dict of node positions
            # labels is a list  of labels of len(pos), to be displayed when hovering the mouse over the nodes
            # color is the color for nodes. When it is set as None the Plotly default color is used
            # size is the size of the dots representing the nodes
            #opacity is a value between [0,1] defining the node color opacity
            L=len(pos)
            trace = Scatter(
                                    x=[], 
                                    y=[], 
                                    text=[],
                                    mode='markers', 
                                    hoverinfo='text',
                                    marker=Marker(
                                        showscale=True,
                                        # colorscale options
                                        # 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' |
                                        # Jet' | 'RdBu' | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'
                                        colorscale='YIGnBu',
                                        reversescale=True,
                                        color=[],         
                                        colorbar=dict(
                                            thickness=15,
                                            title='Node Connections',
                                            xanchor='left',
                                            titleside='right'
                                        ),
                                        line=dict(width=2)))
            for k in range(L):
                trace['x'].append(pos[k][0])
                trace['y'].append(pos[k][1])
            attrib=dict(name='', text=labels , hoverinfo='text') # a dict of Plotly node attributes
            trace=dict(trace, **attrib)# concatenate the dict trace and attrib
            return trace   
            
        
        def make_annotations(pos, text, font_size=14, font_color='rgb(25,25,25)'):
            L=len(pos)
            if len(text)!=L:
                raise ValueError('The lists pos and text must have the same len')
            annotations = Annotations()
            for k in range(L):
                annotations.append(
                    Annotation(
                        text=text[k], 
                        x=pos[k][0], y=pos[k][1],
                        xref='x1', yref='y1',
                        font=dict(color= font_color, size=font_size),
                        showarrow=False)
                )
            return annotations  
            
        links = WikiWeb(self.url).links()
        np_trix = np.array(WikiWeb(self.url).matrix())
        Gr = nx.from_numpy_matrix(np_trix)
        pos = nx.spring_layout(Gr)
        traceE=scatter_edges(Gr, pos)
        traceN=scatter_nodes(pos, labels=links)
        
        for node, adjacencies in enumerate(Gr.adjacency_list()):
            traceN['marker']['color'].append(len(adjacencies))
        
        data1=Data([traceE, traceN])
        fig = Figure(data=data1, layout=Layout(
                title='<br>Wiki Network: '+self.url,
                titlefont=dict(size=16),
                showlegend=False, 
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))
        py.iplot(fig, filename='wiki-network')
        
        
    def shortest_path(self, target):
        
        #checkmark 1
        d0 = time.clock()
        dict_links = {self.url[24:]:WikiWeb(self.url).links()}
        links = WikiWeb(self.url).links()
        wiki = 'https://en.wikipedia.org'
        print(time.clock()-d0)
        
        #checkmark 2
        d0 = time.clock()
        count=0
        while target[24:] not in links:
            link = links[count]
            dict_links.update({link:WikiWeb(wiki+link).links()})
            for link1 in dict_links[link]:
                if link1 not in links:
                    links.append(link1)
            count+=1
        print(time.clock()-d0)
        
        #checkmark 3
        d0 = time.clock()
        gr = nx.from_dict_of_lists(dict_links)
        sp = nx.shortest_path(gr, self.url[24:], target[24:])
        print(time.clock()-d0)
        
        return sp
        
        '''
        To Do:
            1. fix shortest path
            2, be done.
        '''                

