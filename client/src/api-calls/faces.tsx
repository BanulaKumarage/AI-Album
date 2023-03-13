
export function fetchFaces(skip: number, limit: number, sort: string) {
  return fetch(`${process.env.REACT_APP_API}/faces` + '?' + new URLSearchParams({
    limit: limit.toString(),
    skip: skip.toString(),
    sort: sort,
  })).then(res => res.json());
}

export function fetchMediaByFaceId(id: string) {
  return fetch(`${process.env.REACT_APP_API}/faces/${id}`).then(res => res.json());
}
