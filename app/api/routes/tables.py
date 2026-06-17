from typing import Annotated
from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy import inspect,text
from sqlalchemy.orm import Session 
import json

from app.core.db import get_db
from app.models import TableRegistery
from app.schemas import CreateTableRequest,InsertRowRequest 
from app.core.db import engine
from app.api.ddl_helper import build_create_ddl,_serialize



router = APIRouter()

# Here querying is in the old style where it uses traditional orm style.

@router.post('/tables' , tags=["Tables"])
def create_table( db : Annotated[Session , Depends(get_db)] , create_table : CreateTableRequest):

    print("This is the details " , create_table.table_name , create_table.display_name , create_table.columns)
    existing_table = db.query(TableRegistery).filter_by(table_name = create_table.table_name).first()

    if existing_table:
        raise HTTPException(400, f"Table '{create_table.table_name}' already exists in registry.")
    
    inspector = inspect(engine)
    if inspector.has_table(create_table.table_name):
        raise HTTPException(status_code=400,detail=f"Table {create_table.table_name} already exits in the database")
    
    ddl = build_create_ddl(create_table.table_name , create_table.columns)

    try:
        with engine.begin() as conn:
            conn.execute(text(ddl))
    except Exception as e:
        raise HTTPException(500, detail=f"DDL execution failed: {str(e)}")
        

    #Here we initailly create the table and 
    column_snapshot = [c.model_dump() for c in create_table.columns]
    
    registry_entry = TableRegistery(
        table_name = create_table.table_name,
        display_name = create_table.display_name,
        columns_json = json.dumps(column_snapshot)
        
    )
    db.add(registry_entry)
    db.commit()
    db.refresh(registry_entry)

    return _serialize(registry_entry)


@router.get('/tables' , tags=["Tables"])
def get_tables(db : Annotated[Session , Depends(get_db)]):
    rows = db.query(TableRegistery).order_by(TableRegistery.created_at.desc()).all()
    return [_serialize(r) for r in rows]


@router.get("/tables/default")
def get_current_table(db : Annotated[Session , Depends(get_db)]):
    entry = db.query(TableRegistery).filter_by(is_default = True).first()
    if not entry:
        raise HTTPException(status_code=404 , detail="Table not Found")
    
    return _serialize(entry)


@router.get("/tables/rows")
def get_table_row( db : Annotated[Session , Depends(get_db)]):
    entry = db.query(TableRegistery).filter_by(is_default = True).first()

    table_name = entry.table_name

    if not table_name.replace("_","").isalnum():
        raise HTTPException(status_code=400 , detail="Invalid table name")


    if not entry:
        raise HTTPException(status_code=404 , detail="Table not Found")
    

    with engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT * FROM {table_name}")
        )

        rows = [dict(r._mapping) for r in result]

    return {
        "table_name" : entry.table_name,
        "rows" : rows
    }


@router.get("/tables/{table_id}")
def get_table(table_id : int , db : Annotated[Session , Depends(get_db)]):
    row = db.query(TableRegistery).filter_by(id = table_id).first()
    if not row:
        raise HTTPException(status_code=404 , detail="Table not Found")
    return _serialize(row)



@router.get("/tables/{table_id}/cols")
def get_table_cols(table_id : int , db : Annotated[Session , Depends(get_db)]):
    entry = db.query(TableRegistery).filter_by(id = table_id , is_default = True).first()
    if not entry:
        raise HTTPException(status_code=404 , detail="Table not Found")
    
    cols = json.loads(entry.columns_json)

    return cols



@router.patch('/tables/{table_id}/default')
def set_default_table(table_id : int , db : Annotated[Session , Depends(get_db)]):

    target = db.query(TableRegistery).filter_by(id=table_id).first()
    if not target:
        raise HTTPException(404 , "Table not found.")
    
    db.query(TableRegistery).filter(TableRegistery.is_default == True).update({"is_default":False})

    target.is_default = True
    db.commit()
    db.refresh(target)
    return _serialize(target)


@router.delete("/tables/{table_id}")
def delete_table(table_id : int , db : Annotated[Session , Depends(get_db)]):
    row = db.query(TableRegistery).filter_by(id=table_id).first()
    if not row:
        raise HTTPException(404 , "Table not Found")
    
    table_name = row.table_name

    try:
        with engine.connect() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
            conn.commit()
    except Exception as e:
        raise HTTPException(500 , f"Failed to drop table: {str(e)}")
    
    db.delete(row)
    db.commit()


@router.post("/tables/{table_id}/rows")
def bulk_insert(table_id : int ,row_data : InsertRowRequest,  db : Annotated[Session , Depends(get_db)]):
    entry = db.query(TableRegistery).filter_by(id = table_id).first()

    if not entry:
        raise HTTPException(status_code=404 , detail="Table not Found")
    

    allowed_columns = {col['column_name'] for col in json.loads(entry.columns_json)}

    for i , row in enumerate(row_data.data):
        unkown_col = set(row.keys()) - allowed_columns

        if unkown_col:
            raise HTTPException(status_code=400 , detail=f" Row {i} unknown columns {unkown_col}")
    
    col_names = list(allowed_columns)

    batch_size = 2
    total_inserted = 0

    try:
        with engine.begin() as conn:
            sql_query = text(f"INSERT INTO {entry.table_name} ({', '.join(col_names)}) "
                    f"VALUES ({', '.join(f':{c}' for c in col_names)})")
            for i in range(0 , len(row_data.data) , batch_size):
                batch = row_data.data[i : i + batch_size]
                conn.execute(sql_query , batch)
                total_inserted += len(batch)

    except Exception as e:
        raise HTTPException(500, f"Insert failed: {str(e)}")
    

    return {"inserted": len(row_data.data), "table": entry.table_name}

        

    







    











    


    



