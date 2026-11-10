# Reference graphics and sources

Match each dashboard panel to one of these graphics before building it, and follow its discipline.

## Connected scatterplot

"Driving Shifts Into Reverse" (New York Times, 2010) plots miles driven against gas price, one point per year, joined in time order. A connected scatterplot works only when both axes move in one direction over the period. When either axis doubles back, use a line chart.

- https://archive.nytimes.com/www.nytimes.com/imagepages/2010/05/02/business/02metrics.html
- Steve Haroz's research on reading connected scatterplots: http://steveharoz.com/research/connected_scatterplot/

## Small multiples

"How Different Groups Spend Their Day" (Carter, Cox, Quealy and Schoenfeld, 2009). Each panel carries its own direct label, all panels share axes, and there is no legend.

- https://www.nytimes.com/interactive/2009/07/31/business/20080801-metrics-graphic.html

## Beeswarm and distribution

The COVID-19 vaccination tracker beeswarm, and "How 2016 Became Earth's Hottest Year on Record". Draw one dot per record in a single muted color and mark only the summary value. The cloud of dots carries the argument.

- https://www.nytimes.com/interactive/2021/world/covid-vaccinations-tracker.html
- https://www.nytimes.com/interactive/2017/01/18/science/earth/2016-hottest-year-on-record.html

## Bump chart and ranking

Give the leader the hero color and draw the rest in grey. This is the hero rule from `palette.py` applied to ranks over time.

## Practitioners behind the rules

The chart-choice and annotation rules draw on published work and talks by Mike Bostock, Gregor Aisch, Amanda Cox, Kevin Quealy, Adam Pearce and Archie Tse of the Times graphics desk, and on Cynthia Brewer's ColorBrewer ramps.

## Worked example from the source skill

"The World Cup, in four charts" (May 2026) used the martj42 international football results dataset: 964 World Cup matches from 1930 to 2022. It had four panels, each modeled on one graphic above: goals per game by tournament (line), goal difference for eight nations with title years marked (small multiples), every match by total goals banded by era (beeswarm), and the cumulative all-time points table (bump). Each panel carried a one-line note naming its reference. Interaction rules A to E came from bugs found and fixed during that build.

## Provenance

This skill adapts "NYT Data Viz" by the Hyperagent Team, from the Hyperagent marketplace, supplied by the estate owner on 2026-11-08. The adaptation replaced the source's fonts and colors with the neutral profile and a brand override, fixed rendering bugs, and pinned CDN versions. It also added `check_html.py` and the range and progress chart types. It has no affiliation with The New York Times.
