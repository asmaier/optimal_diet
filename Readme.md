# Optimal Diet [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://asmaier-optimal-diet-optimal-diet-6vfi9e.streamlit.app/)

A streamlit app that demonstrates [Stiglers diet](https://en.wikipedia.org/wiki/Stigler_diet). It is one of the first examples of an 
linear optimization problem under constraints which has been solved by the [Simplex algorithm](https://en.wikipedia.org/wiki/Simplex_algorithm).
In 1947 nine clerks needed approximately 120 man days to solve the problem of 9 equations with 77 variables using hand-operated desk calculators 
(see [Dantzig (1990): the diet problem](https://web.archive.org/web/20160411141356/https://dl.dropboxusercontent.com/u/5317066/1990-dantzig-dietproblem.pdf)).

Nowaydays using [Google OR Tools](https://developers.google.com/optimization) (which implements a modern variant of the Simplex algorithm) we can solve the problem
basically in real-time. Therefore the app allows to play with the parameter of the problem. It also allows to optimize not only the price 
as in the original problem, but also the calories and the weight of the food. 
