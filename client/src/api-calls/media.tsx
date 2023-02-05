
export function fetchMediaByAlbum(url: string, skip: number, limit: number, sort: string) {
  return fetch(url + '?' + new URLSearchParams({
    limit: limit.toString(),
    skip: skip.toString(),
    sort: sort
  })).then(res => res.json());
}

export function fetchMediaById(id: string) {
  return fetch(`${process.env.REACT_APP_API}/media/${id}`).then(res => res.json());
}
