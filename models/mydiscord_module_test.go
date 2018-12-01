// Code generated by SQLBoiler (https://github.com/volatiletech/sqlboiler). DO NOT EDIT.
// This file is meant to be re-generated in place and/or deleted at any time.

package models

import (
	"bytes"
	"context"
	"reflect"
	"testing"

	"github.com/volatiletech/sqlboiler/boil"
	"github.com/volatiletech/sqlboiler/queries"
	"github.com/volatiletech/sqlboiler/randomize"
	"github.com/volatiletech/sqlboiler/strmangle"
)

var (
	// Relationships sometimes use the reflection helper queries.Equal/queries.Assign
	// so force a package dependency in case they don't.
	_ = queries.Equal
)

func testMydiscordModules(t *testing.T) {
	t.Parallel()

	query := MydiscordModules()

	if query.Query == nil {
		t.Error("expected a query, got nothing")
	}
}

func testMydiscordModulesDelete(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	if rowsAff, err := o.Delete(ctx, tx); err != nil {
		t.Error(err)
	} else if rowsAff != 1 {
		t.Error("should only have deleted one row, but affected:", rowsAff)
	}

	count, err := MydiscordModules().Count(ctx, tx)
	if err != nil {
		t.Error(err)
	}

	if count != 0 {
		t.Error("want zero records, got:", count)
	}
}

func testMydiscordModulesQueryDeleteAll(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	if rowsAff, err := MydiscordModules().DeleteAll(ctx, tx); err != nil {
		t.Error(err)
	} else if rowsAff != 1 {
		t.Error("should only have deleted one row, but affected:", rowsAff)
	}

	count, err := MydiscordModules().Count(ctx, tx)
	if err != nil {
		t.Error(err)
	}

	if count != 0 {
		t.Error("want zero records, got:", count)
	}
}

func testMydiscordModulesSliceDeleteAll(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	slice := MydiscordModuleSlice{o}

	if rowsAff, err := slice.DeleteAll(ctx, tx); err != nil {
		t.Error(err)
	} else if rowsAff != 1 {
		t.Error("should only have deleted one row, but affected:", rowsAff)
	}

	count, err := MydiscordModules().Count(ctx, tx)
	if err != nil {
		t.Error(err)
	}

	if count != 0 {
		t.Error("want zero records, got:", count)
	}
}

func testMydiscordModulesExists(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	e, err := MydiscordModuleExists(ctx, tx, o.ID)
	if err != nil {
		t.Errorf("Unable to check if MydiscordModule exists: %s", err)
	}
	if !e {
		t.Errorf("Expected MydiscordModuleExists to return true, but got false.")
	}
}

func testMydiscordModulesFind(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	mydiscordModuleFound, err := FindMydiscordModule(ctx, tx, o.ID)
	if err != nil {
		t.Error(err)
	}

	if mydiscordModuleFound == nil {
		t.Error("want a record, got nil")
	}
}

func testMydiscordModulesBind(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	if err = MydiscordModules().Bind(ctx, tx, o); err != nil {
		t.Error(err)
	}
}

func testMydiscordModulesOne(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	if x, err := MydiscordModules().One(ctx, tx); err != nil {
		t.Error(err)
	} else if x == nil {
		t.Error("expected to get a non nil record")
	}
}

func testMydiscordModulesAll(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	mydiscordModuleOne := &MydiscordModule{}
	mydiscordModuleTwo := &MydiscordModule{}
	if err = randomize.Struct(seed, mydiscordModuleOne, mydiscordModuleDBTypes, false, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}
	if err = randomize.Struct(seed, mydiscordModuleTwo, mydiscordModuleDBTypes, false, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = mydiscordModuleOne.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}
	if err = mydiscordModuleTwo.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	slice, err := MydiscordModules().All(ctx, tx)
	if err != nil {
		t.Error(err)
	}

	if len(slice) != 2 {
		t.Error("want 2 records, got:", len(slice))
	}
}

func testMydiscordModulesCount(t *testing.T) {
	t.Parallel()

	var err error
	seed := randomize.NewSeed()
	mydiscordModuleOne := &MydiscordModule{}
	mydiscordModuleTwo := &MydiscordModule{}
	if err = randomize.Struct(seed, mydiscordModuleOne, mydiscordModuleDBTypes, false, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}
	if err = randomize.Struct(seed, mydiscordModuleTwo, mydiscordModuleDBTypes, false, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = mydiscordModuleOne.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}
	if err = mydiscordModuleTwo.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	count, err := MydiscordModules().Count(ctx, tx)
	if err != nil {
		t.Error(err)
	}

	if count != 2 {
		t.Error("want 2 records, got:", count)
	}
}

func mydiscordModuleBeforeInsertHook(ctx context.Context, e boil.ContextExecutor, o *MydiscordModule) error {
	*o = MydiscordModule{}
	return nil
}

func mydiscordModuleAfterInsertHook(ctx context.Context, e boil.ContextExecutor, o *MydiscordModule) error {
	*o = MydiscordModule{}
	return nil
}

func mydiscordModuleAfterSelectHook(ctx context.Context, e boil.ContextExecutor, o *MydiscordModule) error {
	*o = MydiscordModule{}
	return nil
}

func mydiscordModuleBeforeUpdateHook(ctx context.Context, e boil.ContextExecutor, o *MydiscordModule) error {
	*o = MydiscordModule{}
	return nil
}

func mydiscordModuleAfterUpdateHook(ctx context.Context, e boil.ContextExecutor, o *MydiscordModule) error {
	*o = MydiscordModule{}
	return nil
}

func mydiscordModuleBeforeDeleteHook(ctx context.Context, e boil.ContextExecutor, o *MydiscordModule) error {
	*o = MydiscordModule{}
	return nil
}

func mydiscordModuleAfterDeleteHook(ctx context.Context, e boil.ContextExecutor, o *MydiscordModule) error {
	*o = MydiscordModule{}
	return nil
}

func mydiscordModuleBeforeUpsertHook(ctx context.Context, e boil.ContextExecutor, o *MydiscordModule) error {
	*o = MydiscordModule{}
	return nil
}

func mydiscordModuleAfterUpsertHook(ctx context.Context, e boil.ContextExecutor, o *MydiscordModule) error {
	*o = MydiscordModule{}
	return nil
}

func testMydiscordModulesHooks(t *testing.T) {
	t.Parallel()

	var err error

	ctx := context.Background()
	empty := &MydiscordModule{}
	o := &MydiscordModule{}

	seed := randomize.NewSeed()
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, false); err != nil {
		t.Errorf("Unable to randomize MydiscordModule object: %s", err)
	}

	AddMydiscordModuleHook(boil.BeforeInsertHook, mydiscordModuleBeforeInsertHook)
	if err = o.doBeforeInsertHooks(ctx, nil); err != nil {
		t.Errorf("Unable to execute doBeforeInsertHooks: %s", err)
	}
	if !reflect.DeepEqual(o, empty) {
		t.Errorf("Expected BeforeInsertHook function to empty object, but got: %#v", o)
	}
	mydiscordModuleBeforeInsertHooks = []MydiscordModuleHook{}

	AddMydiscordModuleHook(boil.AfterInsertHook, mydiscordModuleAfterInsertHook)
	if err = o.doAfterInsertHooks(ctx, nil); err != nil {
		t.Errorf("Unable to execute doAfterInsertHooks: %s", err)
	}
	if !reflect.DeepEqual(o, empty) {
		t.Errorf("Expected AfterInsertHook function to empty object, but got: %#v", o)
	}
	mydiscordModuleAfterInsertHooks = []MydiscordModuleHook{}

	AddMydiscordModuleHook(boil.AfterSelectHook, mydiscordModuleAfterSelectHook)
	if err = o.doAfterSelectHooks(ctx, nil); err != nil {
		t.Errorf("Unable to execute doAfterSelectHooks: %s", err)
	}
	if !reflect.DeepEqual(o, empty) {
		t.Errorf("Expected AfterSelectHook function to empty object, but got: %#v", o)
	}
	mydiscordModuleAfterSelectHooks = []MydiscordModuleHook{}

	AddMydiscordModuleHook(boil.BeforeUpdateHook, mydiscordModuleBeforeUpdateHook)
	if err = o.doBeforeUpdateHooks(ctx, nil); err != nil {
		t.Errorf("Unable to execute doBeforeUpdateHooks: %s", err)
	}
	if !reflect.DeepEqual(o, empty) {
		t.Errorf("Expected BeforeUpdateHook function to empty object, but got: %#v", o)
	}
	mydiscordModuleBeforeUpdateHooks = []MydiscordModuleHook{}

	AddMydiscordModuleHook(boil.AfterUpdateHook, mydiscordModuleAfterUpdateHook)
	if err = o.doAfterUpdateHooks(ctx, nil); err != nil {
		t.Errorf("Unable to execute doAfterUpdateHooks: %s", err)
	}
	if !reflect.DeepEqual(o, empty) {
		t.Errorf("Expected AfterUpdateHook function to empty object, but got: %#v", o)
	}
	mydiscordModuleAfterUpdateHooks = []MydiscordModuleHook{}

	AddMydiscordModuleHook(boil.BeforeDeleteHook, mydiscordModuleBeforeDeleteHook)
	if err = o.doBeforeDeleteHooks(ctx, nil); err != nil {
		t.Errorf("Unable to execute doBeforeDeleteHooks: %s", err)
	}
	if !reflect.DeepEqual(o, empty) {
		t.Errorf("Expected BeforeDeleteHook function to empty object, but got: %#v", o)
	}
	mydiscordModuleBeforeDeleteHooks = []MydiscordModuleHook{}

	AddMydiscordModuleHook(boil.AfterDeleteHook, mydiscordModuleAfterDeleteHook)
	if err = o.doAfterDeleteHooks(ctx, nil); err != nil {
		t.Errorf("Unable to execute doAfterDeleteHooks: %s", err)
	}
	if !reflect.DeepEqual(o, empty) {
		t.Errorf("Expected AfterDeleteHook function to empty object, but got: %#v", o)
	}
	mydiscordModuleAfterDeleteHooks = []MydiscordModuleHook{}

	AddMydiscordModuleHook(boil.BeforeUpsertHook, mydiscordModuleBeforeUpsertHook)
	if err = o.doBeforeUpsertHooks(ctx, nil); err != nil {
		t.Errorf("Unable to execute doBeforeUpsertHooks: %s", err)
	}
	if !reflect.DeepEqual(o, empty) {
		t.Errorf("Expected BeforeUpsertHook function to empty object, but got: %#v", o)
	}
	mydiscordModuleBeforeUpsertHooks = []MydiscordModuleHook{}

	AddMydiscordModuleHook(boil.AfterUpsertHook, mydiscordModuleAfterUpsertHook)
	if err = o.doAfterUpsertHooks(ctx, nil); err != nil {
		t.Errorf("Unable to execute doAfterUpsertHooks: %s", err)
	}
	if !reflect.DeepEqual(o, empty) {
		t.Errorf("Expected AfterUpsertHook function to empty object, but got: %#v", o)
	}
	mydiscordModuleAfterUpsertHooks = []MydiscordModuleHook{}
}

func testMydiscordModulesInsert(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	count, err := MydiscordModules().Count(ctx, tx)
	if err != nil {
		t.Error(err)
	}

	if count != 1 {
		t.Error("want one record, got:", count)
	}
}

func testMydiscordModulesInsertWhitelist(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Whitelist(mydiscordModuleColumnsWithoutDefault...)); err != nil {
		t.Error(err)
	}

	count, err := MydiscordModules().Count(ctx, tx)
	if err != nil {
		t.Error(err)
	}

	if count != 1 {
		t.Error("want one record, got:", count)
	}
}

func testMydiscordModuleToManyModuleMydiscordGuildModules(t *testing.T) {
	var err error
	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()

	var a MydiscordModule
	var b, c MydiscordGuildModule

	seed := randomize.NewSeed()
	if err = randomize.Struct(seed, &a, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	if err := a.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Fatal(err)
	}

	if err = randomize.Struct(seed, &b, mydiscordGuildModuleDBTypes, false, mydiscordGuildModuleColumnsWithDefault...); err != nil {
		t.Fatal(err)
	}
	if err = randomize.Struct(seed, &c, mydiscordGuildModuleDBTypes, false, mydiscordGuildModuleColumnsWithDefault...); err != nil {
		t.Fatal(err)
	}

	b.ModuleID = a.ID
	c.ModuleID = a.ID

	if err = b.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Fatal(err)
	}
	if err = c.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Fatal(err)
	}

	mydiscordGuildModule, err := a.ModuleMydiscordGuildModules().All(ctx, tx)
	if err != nil {
		t.Fatal(err)
	}

	bFound, cFound := false, false
	for _, v := range mydiscordGuildModule {
		if v.ModuleID == b.ModuleID {
			bFound = true
		}
		if v.ModuleID == c.ModuleID {
			cFound = true
		}
	}

	if !bFound {
		t.Error("expected to find b")
	}
	if !cFound {
		t.Error("expected to find c")
	}

	slice := MydiscordModuleSlice{&a}
	if err = a.L.LoadModuleMydiscordGuildModules(ctx, tx, false, (*[]*MydiscordModule)(&slice), nil); err != nil {
		t.Fatal(err)
	}
	if got := len(a.R.ModuleMydiscordGuildModules); got != 2 {
		t.Error("number of eager loaded records wrong, got:", got)
	}

	a.R.ModuleMydiscordGuildModules = nil
	if err = a.L.LoadModuleMydiscordGuildModules(ctx, tx, true, &a, nil); err != nil {
		t.Fatal(err)
	}
	if got := len(a.R.ModuleMydiscordGuildModules); got != 2 {
		t.Error("number of eager loaded records wrong, got:", got)
	}

	if t.Failed() {
		t.Logf("%#v", mydiscordGuildModule)
	}
}

func testMydiscordModuleToManyAddOpModuleMydiscordGuildModules(t *testing.T) {
	var err error

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()

	var a MydiscordModule
	var b, c, d, e MydiscordGuildModule

	seed := randomize.NewSeed()
	if err = randomize.Struct(seed, &a, mydiscordModuleDBTypes, false, strmangle.SetComplement(mydiscordModulePrimaryKeyColumns, mydiscordModuleColumnsWithoutDefault)...); err != nil {
		t.Fatal(err)
	}
	foreigners := []*MydiscordGuildModule{&b, &c, &d, &e}
	for _, x := range foreigners {
		if err = randomize.Struct(seed, x, mydiscordGuildModuleDBTypes, false, strmangle.SetComplement(mydiscordGuildModulePrimaryKeyColumns, mydiscordGuildModuleColumnsWithoutDefault)...); err != nil {
			t.Fatal(err)
		}
	}

	if err := a.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Fatal(err)
	}
	if err = b.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Fatal(err)
	}
	if err = c.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Fatal(err)
	}

	foreignersSplitByInsertion := [][]*MydiscordGuildModule{
		{&b, &c},
		{&d, &e},
	}

	for i, x := range foreignersSplitByInsertion {
		err = a.AddModuleMydiscordGuildModules(ctx, tx, i != 0, x...)
		if err != nil {
			t.Fatal(err)
		}

		first := x[0]
		second := x[1]

		if a.ID != first.ModuleID {
			t.Error("foreign key was wrong value", a.ID, first.ModuleID)
		}
		if a.ID != second.ModuleID {
			t.Error("foreign key was wrong value", a.ID, second.ModuleID)
		}

		if first.R.Module != &a {
			t.Error("relationship was not added properly to the foreign slice")
		}
		if second.R.Module != &a {
			t.Error("relationship was not added properly to the foreign slice")
		}

		if a.R.ModuleMydiscordGuildModules[i*2] != first {
			t.Error("relationship struct slice not set to correct value")
		}
		if a.R.ModuleMydiscordGuildModules[i*2+1] != second {
			t.Error("relationship struct slice not set to correct value")
		}

		count, err := a.ModuleMydiscordGuildModules().Count(ctx, tx)
		if err != nil {
			t.Fatal(err)
		}
		if want := int64((i + 1) * 2); count != want {
			t.Error("want", want, "got", count)
		}
	}
}

func testMydiscordModulesReload(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	if err = o.Reload(ctx, tx); err != nil {
		t.Error(err)
	}
}

func testMydiscordModulesReloadAll(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	slice := MydiscordModuleSlice{o}

	if err = slice.ReloadAll(ctx, tx); err != nil {
		t.Error(err)
	}
}

func testMydiscordModulesSelect(t *testing.T) {
	t.Parallel()

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	slice, err := MydiscordModules().All(ctx, tx)
	if err != nil {
		t.Error(err)
	}

	if len(slice) != 1 {
		t.Error("want one record, got:", len(slice))
	}
}

var (
	mydiscordModuleDBTypes = map[string]string{`ID`: `integer`, `Name`: `character varying`}
	_                      = bytes.MinRead
)

func testMydiscordModulesUpdate(t *testing.T) {
	t.Parallel()

	if 0 == len(mydiscordModulePrimaryKeyColumns) {
		t.Skip("Skipping table with no primary key columns")
	}
	if len(mydiscordModuleColumns) == len(mydiscordModulePrimaryKeyColumns) {
		t.Skip("Skipping table with only primary key columns")
	}

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	count, err := MydiscordModules().Count(ctx, tx)
	if err != nil {
		t.Error(err)
	}

	if count != 1 {
		t.Error("want one record, got:", count)
	}

	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModulePrimaryKeyColumns...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	if rowsAff, err := o.Update(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	} else if rowsAff != 1 {
		t.Error("should only affect one row but affected", rowsAff)
	}
}

func testMydiscordModulesSliceUpdateAll(t *testing.T) {
	t.Parallel()

	if len(mydiscordModuleColumns) == len(mydiscordModulePrimaryKeyColumns) {
		t.Skip("Skipping table with only primary key columns")
	}

	seed := randomize.NewSeed()
	var err error
	o := &MydiscordModule{}
	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModuleColumnsWithDefault...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Insert(ctx, tx, boil.Infer()); err != nil {
		t.Error(err)
	}

	count, err := MydiscordModules().Count(ctx, tx)
	if err != nil {
		t.Error(err)
	}

	if count != 1 {
		t.Error("want one record, got:", count)
	}

	if err = randomize.Struct(seed, o, mydiscordModuleDBTypes, true, mydiscordModulePrimaryKeyColumns...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	// Remove Primary keys and unique columns from what we plan to update
	var fields []string
	if strmangle.StringSliceMatch(mydiscordModuleColumns, mydiscordModulePrimaryKeyColumns) {
		fields = mydiscordModuleColumns
	} else {
		fields = strmangle.SetComplement(
			mydiscordModuleColumns,
			mydiscordModulePrimaryKeyColumns,
		)
	}

	value := reflect.Indirect(reflect.ValueOf(o))
	typ := reflect.TypeOf(o).Elem()
	n := typ.NumField()

	updateMap := M{}
	for _, col := range fields {
		for i := 0; i < n; i++ {
			f := typ.Field(i)
			if f.Tag.Get("boil") == col {
				updateMap[col] = value.Field(i).Interface()
			}
		}
	}

	slice := MydiscordModuleSlice{o}
	if rowsAff, err := slice.UpdateAll(ctx, tx, updateMap); err != nil {
		t.Error(err)
	} else if rowsAff != 1 {
		t.Error("wanted one record updated but got", rowsAff)
	}
}

func testMydiscordModulesUpsert(t *testing.T) {
	t.Parallel()

	if len(mydiscordModuleColumns) == len(mydiscordModulePrimaryKeyColumns) {
		t.Skip("Skipping table with only primary key columns")
	}

	seed := randomize.NewSeed()
	var err error
	// Attempt the INSERT side of an UPSERT
	o := MydiscordModule{}
	if err = randomize.Struct(seed, &o, mydiscordModuleDBTypes, true); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	ctx := context.Background()
	tx := MustTx(boil.BeginTx(ctx, nil))
	defer func() { _ = tx.Rollback() }()
	if err = o.Upsert(ctx, tx, false, nil, boil.Infer(), boil.Infer()); err != nil {
		t.Errorf("Unable to upsert MydiscordModule: %s", err)
	}

	count, err := MydiscordModules().Count(ctx, tx)
	if err != nil {
		t.Error(err)
	}
	if count != 1 {
		t.Error("want one record, got:", count)
	}

	// Attempt the UPDATE side of an UPSERT
	if err = randomize.Struct(seed, &o, mydiscordModuleDBTypes, false, mydiscordModulePrimaryKeyColumns...); err != nil {
		t.Errorf("Unable to randomize MydiscordModule struct: %s", err)
	}

	if err = o.Upsert(ctx, tx, true, nil, boil.Infer(), boil.Infer()); err != nil {
		t.Errorf("Unable to upsert MydiscordModule: %s", err)
	}

	count, err = MydiscordModules().Count(ctx, tx)
	if err != nil {
		t.Error(err)
	}
	if count != 1 {
		t.Error("want one record, got:", count)
	}
}