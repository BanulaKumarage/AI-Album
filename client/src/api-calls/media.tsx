
const fetchMediaByAlbum = (url: string, skip: number, limit: number, sort: string) => {
  return fetch(url + '?' + new URLSearchParams({
    limit: limit.toString(),
    skip: skip.toString(),
    sort: sort
  })).then(res => res.json());
}

export default fetchMediaByAlbum;
