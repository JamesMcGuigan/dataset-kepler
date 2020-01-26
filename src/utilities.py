import pandas as pd
from pydash import py_ as _

def onehot_encode_comments( dataset: pd.DataFrame, column: str, sep='---', without=['NO_COMMENT'] ) -> pd.DataFrame:
    comments        = dataset[column].apply(lambda str: str.split('---'))
    unique_comments = (
        _(comments.tolist())
            .flatten()
            .uniq()
            .filter()
            .without( * list(without) )
            .sort_by()
            .value()
    )
    onehot = pd.DataFrame(
        comments.map(lambda lst: {
            f'{column}_{key}': int(key in lst) for key in unique_comments
        }).tolist(),
        index=comments.index
    )
    return onehot

