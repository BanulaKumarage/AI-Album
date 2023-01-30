import {
  NavigateFunction,
  Location,
  useLocation,
  useNavigate,
  useParams,
  Params,
  useSearchParams,
} from "react-router-dom";

export interface RouterProps {
  location: Location;
  navigate: NavigateFunction;
  params: Readonly<Params<string>>;
  search: URLSearchParams;
  setSearch: any;
}

export default function withRouter(Component: any) {
  function ComponentWithRouterProp(props: any) {
    let location = useLocation();
    let navigate = useNavigate();
    let params = useParams();
    let [search, setSearch] = useSearchParams();
    return (
    <Component
        {...props}
        router={{ location, navigate, params, search, setSearch }}
    />
    );
  }

  return ComponentWithRouterProp;
}
