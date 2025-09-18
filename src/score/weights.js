export function defaultWeights(){
  return JSON.parse(localStorage.getItem('meta_weights_v1') || '{"ghg":0.4,"water":0.2,"land":0.15,"biodiversity":0.15,"pm":0.05,"eutro":0.05}');
}
export function saveWeights(w){
  localStorage.setItem('meta_weights_v1', JSON.stringify(w));
}
