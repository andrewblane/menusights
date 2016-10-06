from collections import Counter

def ModelIt(menu_item  = 'Default', recipes_returned = []):
  avg_calories = sum([item['recipe_calories'] for item in recipes_returned]) / len(recipes_returned)
  print 'The average nomber of calories is %i' % avg_calories
  ingredient_frequencies = []
  for item in recipes_returned:
      ingredient_frequencies.extend(item["recipe_ingredients"])
  counter = Counter("".join(ingredient_frequencies).split(" "))
  
  columns = 80
  n_occurrences = 10
  to_plot = counter.most_common(n_occurrences)
  labels, values = zip(*to_plot)
  label_width = max(map(len, labels))
  data_width = columns - label_width - 1
  plot_format = '{:%d}|{:%d}' % (label_width, data_width)
  max_value = float(max(values))
  out = []
  for i in range(len(labels)):
    v = int(values[i]/max_value*data_width)
    out.append(plot_format.format(labels[i], '*'*v))

  result = {"calories": avg_calories,
            "ingredients": out}
  if menu_item != 'Default':
    return result
  else:
    return 'check your input'