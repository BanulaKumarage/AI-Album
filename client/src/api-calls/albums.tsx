const fetchAlbums = (skip: number, limit: number, sort: string) => {
  return fetch(`${process.env.REACT_APP_API}/albums` + '?' + new URLSearchParams({
    limit: limit.toString(),
    skip: skip.toString(),
    sort: sort
  })).then(res => res.json());
}

export default fetchAlbums;
