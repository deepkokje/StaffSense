import { useState } from "react";

import type { BringToBandMinQuery, RaiseCostQuery } from "../api/types";

export function useWhatIfState() {
  const [bandQuery, setBandQuery] = useState<BringToBandMinQuery>({});
  const [raiseQuery, setRaiseQuery] = useState<RaiseCostQuery>();

  function changeBandCountries(country: string[]) {
    setBandQuery(country.length ? { country } : {});
  }

  return { bandQuery, raiseQuery, changeBandCountries, submitRaise: setRaiseQuery };
}
