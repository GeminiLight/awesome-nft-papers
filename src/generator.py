import csv
import os
import copy
import shutil

abbr = {
    # 'Overview': 'Overview', 
    # 'Graph Analysis': 'Graph Analysis', 
    # 'Valuation & Price Prediction': 'Valuation-Price-Prediction', 
    # 'Investment': 'Investment', 
    # 'Fraud Detection': 'Fraud-Detection',
    # 'Anomaly Detection': 'AD', 
    # 'Recommendation': 'Recommendation', 
    # 'Generation': 'Generation', 
    # 'Visualization': 'Visualization', 
    # 'Other': 'Other', 
}


def md2csv(mdFile, csvFile):  # From the md file to generate a csv file that contains the paper list.
    f = open(mdFile)
    line = f.readline()
    problem_start = False
    paper_list = []
    category = None
    while line:
        print(line)
        if problem_start and "### [" in line:
            category = line[line.find("[") + 1: line.find("]")]
        if problem_start and '0' <= line[0] <= '9':
            new_paper = ["" for _ in range(7)]  # 0 category, 1 title, 2 publisher, 3 year, 4 type, 5 link, 6 authors;
            new_paper[0] = category
            index = 1
            i = -1
            while i + 1 < len(line):
                i += 1
                if i < line.find(". **") + 4:
                    continue
                new_paper[index] += line[i]
                if i == line.find(".**") and index == 1:  # title -> publisher
                    i += 3
                    index += 1
                    continue
                if line[i + 1] == "," and index == 2:  # publisher -> year
                    i += 2
                    index += 1
                    continue
                if line[i + 1] == "." and index == 3:  # year -> type
                    i += 3
                    index += 1
                    continue
                if line[i + 1] == "]" and index == 4:  # type -> link
                    i += 2
                    index += 1
                    continue
                if line[i + 1] == ")" and index == 5:  # link->authors
                    index += 1
                    break
            assert index == 6
            _ = f.readline()
            line = f.readline()
            new_paper[index] = line[line.find('*') + 1:-2]
            paper_list.append(new_paper)

        if "</table>" in line:
            problem_start = True
        line = f.readline()
    f.close()
    with open(csvFile, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["category", "title", "publisher", "year", "type", "link", "authors"])
        for paper in paper_list:
            writer.writerow(paper)


def sort_by_time(elem):
    return elem[3]


def csv2md(csvFile, mdFile, header):
    csvFile = open(csvFile, "r", encoding='utf-8')
    reader = csv.reader(csvFile)
    raw_papers = []
    papers = []
    for item in reader:
        if reader.line_num == 1:
            continue
        raw_papers.append(item)
    csvFile.close()

    classes = []
    for paper in raw_papers:
        if ";" in paper[0]:
            paper_classes = paper[0].split(";")
            paper_classes = [cls.strip() for cls in paper_classes]
        else:
            paper_classes = [paper[0].strip()]
        for cls in paper_classes:
            if cls not in classes:
                classes.append(cls)

    for c in classes:
        p = []
        for paper in raw_papers:
            if c in paper[0]:
                new_paper = copy.deepcopy(paper)
                new_paper[0] = c
                p.append(new_paper)
        p.sort(key=sort_by_time)
        papers = papers + p
    # command = "cp " + header + " " + mdFile
    # os.system(command)
    shutil.copy(header, mdFile)
    with open(mdFile, "a", encoding='utf-8') as file:
        # write category
        for i in range(len(classes) // 2):
            name1 = classes[2 * i + 1]
            name_index1 = classes[2 * i + 1].replace(" ", "-").lower()
            file.writelines('<tr>\n')
            if name1 in abbr:
                file.writelines('\t<td>&emsp;<a href=#{}>2.{} {} ({})</a></td>\n'.format(name_index1, 2 * i + 1, name1,
                                                                                         abbr[name1]))
            else:
                file.writelines('\t<td>&emsp;<a href=#{}>2.{} {}</a></td>\n'.format(name_index1, 2 * i + 1, name1))
            if 2 * i + 1 < len(classes) - 1:
                name2 = classes[2 * i + 2]
                name_index2 = classes[2 * i + 2].replace(" ", "-").lower()
                if name2 in abbr:
                    file.writelines(
                        '\t<td>&emsp;<a href=#{}>2.{} {} ({})</a></td>\n'.format(name_index2, 2 * i + 2, name2,
                                                                                 abbr[name2]))
                else:
                    file.writelines('\t<td>&emsp;<a href=#{}>2.{} {}</a></td>\n'.format(name_index2, 2 * i + 2, name2))
            else:
                file.writelines('<td>&ensp;</td>\n')
            file.writelines('</tr>\n')
        file.writelines('</table>\n')

        # write content
        file.write('\n')
        file.write('\n')
        file.write('\n')
        file.write('\n')
        num = 0
        category = papers[0][0]
        file.writelines("### [{}](#content)".format(category))
        file.write('\n')
        file.write('\n')
        for paper in papers:
            paper = [p.strip() for p in paper]
            if paper[0] != category:
                if category == "Overview":
                    file.writelines("## [Tasks](#content)")
                    file.write('\n')
                    file.write('\n')
                category = paper[0]
                file.writelines("### [{}](#content)".format(category))
                file.write('\n')
                file.write('\n')
                num = 0
            num += 1
            # "category", "title", "publisher", "year", "type", "link", "authors, *code"
            file.writelines(f'{num}. **{paper[1]}**')
            file.write('\n')
            file.write('\n')
            file.writelines("    *{}*".format(paper[6]))
            # if paper[7] == "":
            #     # file.writelines(
            #     #     f'{num}. **{paper[1]}** {paper[2]}, {paper[3]}. [{paper[4]}]({paper[5]})')
            #     file.writelines(
            #         "{}. **{}** {}, {}. [{}]({})".format(num, paper[1], paper[2], paper[3], paper[4], paper[5]))
            # else:
            #     file.writelines(
            #         "{}. **{}** {}, {}. [{}]({}), [code]({})".format(num, paper[1], paper[2], paper[3], paper[4],
            #                                                          paper[5], paper[7]))
            file.write('\n')
            file.write('\n')
            file.writelines(f'    {paper[2]}, {paper[3]}. [`{paper[4]}`]({paper[5]})')
            if paper[7] != "":
                file.writelines(f', [`code`]({paper[7]})')
            file.write('\n')
            file.write('\n')

def visualize(csvFile):
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    import plotly.express as px
    import plotly.graph_objects as go
    
    
    if theme == 'dark':
        plt.style.use('dark_background')
        plotly_template = 'plotly_dark'
    else:
        plt.style.use('default')

    df_papers = pd.read_csv(csvFile)
    width = 800
    height = 800
    top_conference_list = ['KDD', 'WWW', 'SIGIR', 'CCS', 'CHI', 'MM', 'NeurIPS', 'CSCW']

    # Figure 1: Annual Count Trend
    df_paper_groupby_year_type_for_count = df_papers.groupby(["year", "type"]).count().reset_index().rename({'title': 'count'}, axis=1)
    df_paper_groupby_year_type_for_count = df_paper_groupby_year_type_for_count[['year', 'type', 'count']]
    df_paper_groupby_year_type_for_count['year'] = df_paper_groupby_year_type_for_count['year'].astype(str)
    df_paper_groupby_year_type_for_count = df_paper_groupby_year_type_for_count.pivot(index='year', columns='type', values='count').fillna(0).astype(int)
    df_paper_groupby_year_type_for_count = df_paper_groupby_year_type_for_count.reset_index()
    publication_type_list = df_papers.type.unique().tolist()

    fig = px.bar(df_paper_groupby_year_type_for_count, 
                    x="year", y=publication_type_list, 
                    title="Annual Count Trend",
                    color_discrete_sequence=px.colors.sequential.dense[1::2],
                    width=width, height=height,
                    template=plotly_template)
    fig.write_image("../figures/annual_count_trend.svg")

    # Figure 2: Category Distribution
    df_papers_groupby_category_for_count = df_papers.groupby(["category"]).count().reset_index().rename({'title': 'count'}, axis=1)
    fig = px.pie(df_papers_groupby_category_for_count, values='count', names='category', 
                    title='Category Distribution', 
                    # color_discrete_sequence= px.colors.sequential.Plasma_r,
                    # color_discrete_sequence= px.colors.sequential.Plasma_r,
                    width=width, height=height,
                    template=plotly_template)
    fig.update_traces(textposition='inside', textinfo='label+percent+value')
    fig.write_image("../figures/category_distribution.svg")

    # Figure 3: Publisher Distribution
    def get_publisher_type(paper_info):
        if paper_info['type'] != 'conference':
            return paper_info['type'].capitalize()
        else:
            if paper_info['publisher'] in top_conference_list:
                return 'Top Conference'
            else:
                return 'Other Conference'
                
    df_papers_groupby_publisher_for_count = df_papers.groupby(["publisher"]).agg({'title': 'count', 'type': 'first'}).reset_index().rename({'title': 'count'}, axis=1)
    df_papers_groupby_publisher_for_count['publisher_type'] = df_papers_groupby_publisher_for_count.apply(get_publisher_type, axis=1)
    df_papers_groupby_publisher_type_for_count = df_papers_groupby_publisher_for_count.groupby(["publisher_type"]).agg({'count': 'sum'}).reset_index()

    sunburst_labels = ['NFT']
    sunburst_parents = ['']
    sunburst_values = [0]
    sunburst_labels += df_papers_groupby_publisher_type_for_count['publisher_type'].values.tolist()
    sunburst_parents += ['NFT'] * len(df_papers_groupby_publisher_type_for_count)
    sunburst_values += [0] * len(df_papers_groupby_publisher_type_for_count)
    sunburst_labels += df_papers_groupby_publisher_for_count['publisher'].values.tolist()
    sunburst_parents += df_papers_groupby_publisher_for_count['publisher_type'].values.tolist()
    sunburst_values += df_papers_groupby_publisher_for_count['count'].values.tolist()

    fig =go.Figure(go.Sunburst(
        labels=sunburst_labels,
        parents=sunburst_parents,
        values=sunburst_values,
    )
    )
    fig.update_layout(
        # margin = dict(t=0, l=0, r=0, b=0), 
        title="Publisher Distribution",
        width=width, height=height,
        template=plotly_template
        )
    fig.write_image("../figures/publisher_distribution.svg")

    # Figure 4: Title Word Cloud
    title_list = df_papers.title.tolist()
    sentence = ' '.join(title_list)
    terms_to_replace = [
        'NFTs', 'nfts', 'Nfts',
        'NFT\'s', 'nft\'s', 'Nft\'s',
        'NFT', 'nft', 'Nft',
        'Non-fungible', 'non-fungible', 'Non-Fungible',
        'Tokens', 'tokens',
        'Token\'s', 'token\'s', 'Tokens\'', 'tokens\'',
        'Token', 'token', 
        'Use', 'Using', 'Via'
    ]
    for term in terms_to_replace:
        sentence = sentence.replace(term, '')
    wc = WordCloud(width=800, height=800).generate(sentence)
    plt.figure(figsize=(10, 10), dpi=100)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.title("Title Word Cloud", fontsize=18)
    plt.savefig("../figures/title_word_cloud.png", dpi=200)


if __name__ == '__main__':
    # md2csv("../README.md", "../data/papers.csv")
    theme = 'dark'
    csv2md("../data/papers.csv", "../README.md", "../data/header.md")
    visualize("../data/papers.csv")
